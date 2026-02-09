#!/usr/bin/env python3
"""
Public (no-credentials) pull of binary assets from Google Drive after clone.

Requires: manifests/public_index.json committed in repo.
Usage:
  poetry run python -m Src.Cloud.scripts.public_pull
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
from pathlib import Path
from Src.Utils.utils import human_size, sha256_of_file, RED_TXT, GREEN_TXT, DEFAULT_TXT

SCRIPT_DIR = Path(__file__).resolve().parent
CLOUD_DIR = SCRIPT_DIR.parent
MANIFESTS_DIR = CLOUD_DIR / "manifests"
INDEX_PATH = MANIFESTS_DIR / "public_index.json"
REPO_ROOT = CLOUD_DIR.parent.parent

DRIVE_UC = "https://drive.google.com/uc?export=download&id={file_id}"

CONFIRM_RE = re.compile(r"confirm=([0-9A-Za-z_]+)")

def _open_url(url: str, cj: CookieJar) -> urllib.response.addinfourl:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return opener.open(req)

def download_drive_file(file_id: str, out_path: Path) -> None:
    """
    Download a public Drive file by file_id.
    Handles the large-file "confirm" interstitial.
    Writes atomically via temp file.
    """
    cj = CookieJar()
    url = DRIVE_UC.format(file_id=file_id)

    resp = _open_url(url, cj)
    ct = (resp.headers.get("Content-Type") or "").lower()

    # If HTML, likely needs confirm token
    if "text/html" in ct:
        html = resp.read().decode("utf-8", errors="ignore")
        m = CONFIRM_RE.search(html)
        if not m:
            raise RuntimeError(f"Drive download blocked or not public (no confirm token). file_id={file_id}")
        token = m.group(1)
        url2 = url + "&confirm=" + urllib.parse.quote(token)
        resp = _open_url(url2, cj)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(prefix=out_path.name + ".", dir=str(out_path.parent))
    os.close(fd)
    tmp = Path(tmp_name)

    try:
        with tmp.open("wb") as f:
            shutil.copyfileobj(resp, f, length=1024 * 1024)
        tmp.replace(out_path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass

def main() -> int:

    # Check index exists and is valid
    if not INDEX_PATH.exists():
        print(f"ERROR: Missing {INDEX_PATH}. You need to run the credentialed sync once and commit public_index.json.")
        return 2

    # Load and validate index
    items: list[dict] = json.loads(INDEX_PATH.read_text(encoding="utf8"))
    if not isinstance(items, list):
        print("ERROR: public_index.json must be a list.")
        return 2

    # Pre-download plan and summary
    to_download = []
    to_skip = []
    total_size = 0
    for it in items:
        repo_rel = it.get("path_relative_to_root")
        fid = it.get("drive_file_id")
        expected = (it.get("sha256") or "").lower()
        size = int(it.get("size_in_bytes", 0) or 0)

        if not repo_rel or not fid:
            continue

        dst = REPO_ROOT / repo_rel

        if dst.exists() and expected:
            try:
                if dst.is_file() and sha256_of_file(dst).lower() == expected:
                    to_skip.append(repo_rel)
                    continue
            except Exception:
                pass

        to_download.append(repo_rel)
        total_size += size

    print("============= Public pull plan =============")
    print(f"Files in index:      {len(items)}")
    print(f"Files to download:   {len(to_download)}")
    print(f"Files to skip:       {len(to_skip)}")
    print(f"Total download size: {human_size(total_size)}")
    print("============================================\n")

    # Iterate items and pull as needed
    total = 0
    done = 0
    skipped = 0
    for idx, it in enumerate(items, start=1):

        repo_rel = it.get("path_relative_to_root")
        fid = it.get("drive_file_id")
        expected = (it.get("sha256") or "").lower()
        size = int(it.get("size_in_bytes", 0) or 0)

        if not repo_rel or not fid:
            print("WARNING: invalid item in public json, missing path_relative_to_root or drive_file_id.")
            print(f"Item: {it}")
            if input("Would you like to skip this item? (y/n) ").lower() == "y":
                continue
            raise RuntimeError(f"Invalid item in public_index.json: {it}")

        dst: Path = REPO_ROOT / repo_rel
        repo_rel_str = ("..." if len(repo_rel) > 60 else "") + repo_rel[-60:]
        total += 1

        if dst.exists() and expected:
            # If file exists, check if it's a file and if sha256 matches expected.
            if not dst.is_file():
                print(f"WARNING: destination exists but is not a file: {dst}")
                print(f"Repo path: {repo_rel}")
                print(f"Expected sha256: {expected}")
                ans = input("Skip this item? (y/n) ").strip().lower()
                if ans == "y":
                    skipped += 1
                    print(f"[{idx}]\t{RED_TXT}skip{DEFAULT_TXT}\t{repo_rel_str} (destination exists but is not a file)")
                    continue
                raise RuntimeError(f"Destination exists but is not a file: {dst}")

            try:
                got = sha256_of_file(dst).lower()
            except Exception as e:
                print(f"WARNING: failed to compute sha256 for existing file: {dst}")
                print(f"Repo path: {repo_rel}")
                print(f"Expected sha256: {expected}")
                print(f"Error: {type(e).__name__}: {e}")
                ans = input("Continue download anyway (treat as needing download)? (y/n) ").strip().lower()
                if ans == "y":
                    # proceed to download/overwrite below (do not continue)
                    pass
                else:
                    raise

            else:
                if got == expected:
                    skipped += 1
                    print(f"[{idx}]\t{RED_TXT}skip{DEFAULT_TXT}\t{repo_rel_str} (file exists and sha256 matches)")
                    continue
                else:
                    print(f"WARNING: file exists but sha256 does NOT match: {dst}")
                    print(f"Repo path: {repo_rel}")
                    print(f"Expected sha256: {expected.lower()}")
                    print(f"Actual sha256:   {got}")
                    ans = input("Re-download and overwrite this file? (y/n) ").strip().lower()
                    if ans == "y":
                        # proceed to download/overwrite below
                        pass
                    else:
                        raise RuntimeError(f"Hash mismatch for {repo_rel_str}, and user chose not to re-download.")

        print(f"[{idx}]\t{GREEN_TXT}pull{DEFAULT_TXT}\t{repo_rel_str} ({human_size(size) if size else '??'})")
        download_drive_file(fid, dst)
        done += 1

        if expected:
            got = sha256_of_file(dst).lower()
            if got != expected:
                print(f"WARNING: sha256 mismatch after download")
                print(f"Repo path: {repo_rel}")
                print(f"Expected:  {expected}")
                print(f"Actual:    {got}")

                ans = input("Try downloading again (overwrite)? (y/n) ").strip().lower()
                if ans == "y":
                    download_drive_file(fid, dst)
                    got2 = sha256_of_file(dst).lower()
                    if got2 != expected:
                        raise RuntimeError(
                            f"Hash mismatch persists for {repo_rel_str}\n  expected={expected}\n  got={got2}"
                        )
                else:
                    raise RuntimeError(f"Hash mismatch for {repo_rel_str}, and user chose not to re-download.")

    print(f"\nPublic pull complete. total={total}, downloaded={done}, skipped={skipped}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
