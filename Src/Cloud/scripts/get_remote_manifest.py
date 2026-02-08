#!/usr/bin/env python3
"""Script to fetch the latest manifest from Google Drive and save it locally."""

from __future__ import annotations
import io
import json
import sys
from pathlib import Path
from typing import Optional
from Src.Utils.utils import RED_TXT, DEFAULT_TXT

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
CLOUD_DIR = SCRIPT_DIR.parent
MANIFESTS_DIR = CLOUD_DIR / "manifests"
CREDS_DIR = CLOUD_DIR / "creds"
CREDS_PATH = CREDS_DIR / "credentials.json"
TOKEN_PATH = CREDS_DIR / "token.json"
OUT_PATH = MANIFESTS_DIR / "remote_manifest.json"
DRIVE_FOLDER_NAME = "to_infinity_and_beyond_assets"
MANIFEST_FILENAME = "remote_manifest.json"

# Utils
def get_service():
    """Authenticate and return a Google Drive service instance."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except Exception:
        print("Google Drive libraries missing. Install deps in Poetry venv.", file=sys.stderr)
        sys.exit(2)

    if not CREDS_PATH.exists():
        print(f"{RED_TXT}Missing creds: {CREDS_PATH}{DEFAULT_TXT}", file=sys.stderr)
        sys.exit(2)

    SCOPES = ["https://www.googleapis.com/auth/drive"]

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf8")

    return build("drive", "v3", credentials=creds, cache_discovery=False)

def find_folder_id_by_name(service, name: str) -> Optional[str]:
    """Find a folder ID by its name. Returns None if not found."""
    q = (
        "name = '{}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        .format(name.replace("'", "\\'"))
    )
    res = service.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def find_file_id_in_folder(service, parent_id: str, filename: str) -> Optional[str]:
    """Find a file ID by its name within a specific folder. Returns None if not found."""
    q = (
        "'{}' in parents and name = '{}' and trashed = false"
        .format(parent_id, filename.replace("'", "\\'"))
    )
    res = service.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def download_file_text(service, file_id: str) -> str:
    """Download a file's content as text given its ID."""
    from googleapiclient.http import MediaIoBaseDownload

    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    return fh.getvalue().decode("utf8", errors="strict")

# Main
def main():
    # Sanity checks
    if not CREDS_DIR.exists():
        print(f"{RED_TXT}Missing creds dir: {CREDS_DIR}{DEFAULT_TXT}", file=sys.stderr)
        sys.exit(2)
    if not MANIFESTS_DIR.exists():
        print(f"{RED_TXT}Missing manifests dir: {MANIFESTS_DIR}{DEFAULT_TXT}", file=sys.stderr)
        sys.exit(2)

    # Get Drive service
    service = get_service()

    # Find folder
    folder_id = find_folder_id_by_name(service, DRIVE_FOLDER_NAME)
    if not folder_id:
        print(f"{RED_TXT}Drive folder not found: {DRIVE_FOLDER_NAME}{DEFAULT_TXT}", file=sys.stderr)
        sys.exit(2)

    # Find manifest file in folder
    manifest_id = find_file_id_in_folder(service, folder_id, MANIFEST_FILENAME)
    if not manifest_id:
        print(f"{RED_TXT}Manifest not found in {DRIVE_FOLDER_NAME}: {MANIFEST_FILENAME}{DEFAULT_TXT}", file=sys.stderr)
        sys.exit(2)

    # Download manifest content as text
    text = download_file_text(service, manifest_id)

    # Validate JSON (fail fast if garbage)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        if not text.strip():
            data = {}
        else:
            print(f"{RED_TXT}Failed to parse JSON: {e}{DEFAULT_TXT}", file=sys.stderr)
            sys.exit(2)

    # Save to disk
    OUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf8")
    print(f"Saved remote manifest -> {OUT_PATH}")

# Entry point
if __name__ == "__main__":
    raise SystemExit(main()) # Return code from main()
