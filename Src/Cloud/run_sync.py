#!/usr/bin/env python3
"""
Simple wrapper to run the cloud syncronization pipeline and print concise stats.

Usage:
  python Utils/Cloud/run_sync.py 

Behavior:
- Runs generate_local_manifest.py and get_remote_manifest.py (prints outputs).
- Reads local_manifest.json and remote_manifest.json and prints totals and differences.
- Askes wheather user wants to syncronize repo with cloud.
- Syncronizesation is done by sync.py which will upload new files and update mismatched files based on the local and remote manifests.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
from Src.Utils.utils import human_size, RED_TXT, DEFAULT_TXT

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PY = sys.executable
LOCAL_MANIFEST_PATH = SCRIPT_DIR / "manifests" / "local_manifest.json"
REMOTE_MANIFEST_PATH = SCRIPT_DIR / "manifests" / "remote_manifest.json"
GENERATE_LOCAL_MAINIFEST_PATH = SCRIPT_DIR / "scripts" / "generate_local_manifest.py"
SYNC_PATH = SCRIPT_DIR / "scripts" / "sync_drive.py"

# Utils
def load_json(path: Path):
    """Load JSON from file, return empty list if file doesn't exist."""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf8"))

def canon(d: dict) -> str:
    """Canonicalize dict to JSON string with sorted keys and no whitespace."""
    return json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def summarize(local: List[Dict], remote: List[Dict]) -> Dict:
    """
    Summarize local and remote manifests, return dict with counts and lists of differences.
    Each item in local and remote is expected to be a dict with:
    - "name": file name
    - "path_relative_to_root": relative path of the file
    - "size_in_bytes": size of the file in bytes
    - "sha256": sha256 hash of the file

    returns a dict with:
    - "local_count": number of local files  
    - "remote_count": number of remote files
    - "local_bytes": total size of local files in bytes
    - "remote_bytes": total size of remote files in bytes
    - "to_upload": list of local items that are not in remote (new files)
    - "to_update": list of local items that are in remote but have different sha256 (mismatched files)
    """
    local_set  = {canon(d) for d in local}
    remote_set = {canon(d) for d in remote}

    return {
        "local_count": len(local),
        "remote_count": len(remote),
        "local_bytes": sum(it.get("size_in_bytes", 0) for it in local),
        "remote_bytes": sum(it.get("size_in_bytes", 0) for it in remote),
        "to_upload": [d for d in local  if canon(d) not in remote_set],
        "to_archive": [d for d in remote if canon(d) not in local_set],
    }

def print_summary(s):
    """Print summary of local and remote manifests and differences."""

    print("\n=== Summary ===")
    print(f"Local:  {s['local_count']} files, {human_size(s['local_bytes'])}")
    print(f"Remote: {s['remote_count']} files, {human_size(s['remote_bytes'])}")

    if not s["to_upload"] and not s["to_archive"]:
        print("Status: Everything up to date. No uploads, updates or archiving needed.")
        return
    
    if s["to_upload"]:
        print(f"{len(s['to_upload'])} new files to upload:")
        for i, p in enumerate(s["to_upload"][:100], start=1):
            print(f"  + {i} {p["path_relative_to_root"]}")
        if len(s["to_upload"]) > 100:
            print("  ...", len(s["to_upload"]) - 100, "more")
    
    if s["to_archive"]:
        print(f"{len(s['to_archive'])} files to archive (exist in remote but not local):")
        for i, p in enumerate(s["to_archive"][:100], start=1):
            print(f"  - {i} {p['path_relative_to_root']}")
        if len(s["to_archive"]) > 100:
            print("  ...", len(s["to_archive"]) - 100, "more")

# Main
def main():
    # Generate local manifest
    print("\n>>> Generating local manifest...")
    rc = subprocess.run([PY, "-m", "Src.Cloud.scripts.generate_local_manifest"]).returncode
    if rc != 0:
        print(f"{RED_TXT}generate_local_manifest.py failed (return code={rc}). Aborting.{DEFAULT_TXT}")
        sys.exit(rc)

    # Build remote index (prefer upload_map.csv)
    print("\n>>> Building remote index...")
    rc = subprocess.run([PY, "-m", "Src.Cloud.scripts.get_remote_manifest"]).returncode
    if rc != 0:
        print(f"{RED_TXT}get_remote_manifest.py failed (return code={rc}). Aborting.{DEFAULT_TXT}")
        sys.exit(rc)

    # Load manifests and compute summary
    summary = summarize(load_json(LOCAL_MANIFEST_PATH), load_json(REMOTE_MANIFEST_PATH))
    print_summary(summary)

    if not (summary["to_upload"] or summary["to_archive"]):
        print("\nNo changes to apply. ")
        return

    # Ask user if they want to apply changes
    response = input("\nWould you like to apply these changes? (y/n) ").strip().lower()
    if response not in ("y", "yes"):
        print("Aborted.")
        return
    
    else:
        print("\n>>> Applying changes (this will upload/archive files)...")
        rc = subprocess.run([PY, "-m", "Src.Cloud.scripts.sync"]).returncode
        if rc != 0:
            print(f"{RED_TXT}sync_drive.py failed (rc={rc}).{DEFAULT_TXT}")
            sys.exit(rc)
            
        print("Cloud synchronization complete.")

# Entry point
if __name__ == "__main__":
    main()