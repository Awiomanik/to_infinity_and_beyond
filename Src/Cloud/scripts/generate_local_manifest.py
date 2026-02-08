#!/usr/bin/env python3
"""Generate a manifest of local files in the repo, excluding git-ignored files."""

from __future__ import annotations
import json
from pathlib import Path
from typing import List, Set
from Src.Utils.utils import sha256_of_file, human_size, RED_TXT, DEFAULT_TXT, BINARY_EXTS

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
CLOUD_DIR = SCRIPT_DIR.parent
MANIFESTS_PATH = CLOUD_DIR / "manifests"
OUT_PATH = MANIFESTS_PATH / "local_manifest.json"
ROOT_DIR = CLOUD_DIR.parent.parent
GIT_IGNORE_PATH = ROOT_DIR / ".gitignore"

# Utils
def parse_cloud_asset_extensions() -> Set[str]:
    """
    Parse .gitignore and extract file extensions listed under the CLOUD_ASSETS section.
    Returns a set like: {"png", "jpg", "mp4", ...}
    """
    exts: Set[str] = set()
    in_cloud_section = False

    for raw_line in GIT_IGNORE_PATH.read_text(encoding="utf8").splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("#"):
            if line.strip() == "# CLOUD_ASSETS":
                in_cloud_section = True
            continue

        if not in_cloud_section:
            continue

        # Only accept patterns like "*.ext"
        if line.startswith("*.") and "/" not in line:
            ext = line[2:].strip().lower()
            if ext:
                exts.add(ext)

    return exts

def find_files() -> List[Path]:
    """
    Recursively find all files in the root directory, 
    excluding .git and non-binary files
    and files in .gitignore that are not binary (based on .gitignore structure).
    """
    ignored_exts = parse_cloud_asset_extensions()

    out = []
    for p in ROOT_DIR.rglob("*"):
        if not p.is_file():
            continue
        if ".git" in p.parts:
            continue
        if p.suffix.lower() in ignored_exts:
            continue
        if p.suffix.lower() in BINARY_EXTS:
            out.append(p)
    return sorted(out)

# Main
def main():
    # Check paths
    if not GIT_IGNORE_PATH.is_file():
        print(f"{RED_TXT}Error: Git ignore file {GIT_IGNORE_PATH} does not exist.{DEFAULT_TXT}")
        return
    if not MANIFESTS_PATH.is_dir():
        print(f"{RED_TXT}Error: Output directory {MANIFESTS_PATH} does not exist.{DEFAULT_TXT}")
        return
    
    # Find files (and filter by git ignore)
    files = find_files()

    # Generate manifest
    results = []
    for p in files:
        rel = p.relative_to(ROOT_DIR).as_posix()
        results.append({
            "name": p.name,
            "path_relative_to_root": rel,
            "size_in_bytes": p.stat().st_size,
            "sha256": sha256_of_file(p)
        })
    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf8")
    total = sum(x["size_in_bytes"] for x in results)
    print(f"Local: {len(results)} files, {human_size(total)}")

# Entry point
if __name__ == "__main__":
    raise SystemExit(main()) # Return code from main()