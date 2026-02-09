#!/usr/bin/env python3
"""Sync local assets with remote Google Drive storage."""
from __future__ import annotations
import json
from pathlib import Path, PurePosixPath
from datetime import timezone, datetime
from googleapiclient.http import MediaInMemoryUpload, MediaFileUpload
from Src.Utils.utils import sha256_of_file

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
CLOUD_DIR = SCRIPT_DIR.parent
MANIFESTS_DIR = CLOUD_DIR / "manifests"
LOCAL_MANIFEST_PATH = MANIFESTS_DIR / "local_manifest.json"
REMOTE_INDEX_PATH = MANIFESTS_DIR / "remote_manifest.json" 
REPO_ROOT = CLOUD_DIR.parent.parent

# Drive layout Paths
DRIVE_ROOT_FOLDER_NAME = "to_infinity_and_beyond_assets"
DRIVE_ASSETS_FOLDER_NAME = "assets"
DRIVE_ARCHIVE_FOLDER_NAME = "archive"
DRIVE_MANIFEST_FILENAME = "remote_manifest.json"

# Utils
def append_cloud_sync_log(
    upload_count: int,
    archive_count: int,
    local_manifest: Path,
    remote_manifest: Path,
):
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"
    local_hash = sha256_of_file(local_manifest)
    remote_hash = sha256_of_file(remote_manifest)

    line = (
        f"{timestamp} | "
        f"UPLOAD={upload_count} | "
        f"ARCHIVE={archive_count} | "
        f"LOCAL_HASH={local_hash} | "
        f"REMOTE_HASH={remote_hash}\n"
    )

    log_path = CLOUD_DIR / "sync_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)
        f.flush()

def load_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf8"))

def same(local: dict, remote: dict) -> bool:
    # prefer sha if both present
    ls, rs = local.get("sha256"), remote.get("sha256")
    if ls and rs:
        return ls == rs
    return int(local.get("size") or 0) == int(remote.get("size") or 0)

def canon(d: dict) -> str:
    """Canonicalize dict to JSON string with sorted keys and no whitespace."""
    return json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def plan(local: list[dict], remote: list[dict]) -> tuple[list[str], list[str]]:
    """
    Returns:
      to_archive: remote extras + remote mismatches (all moved to archive)
      to_upload:  local-only files to upload
    
    Each item in local and remote is expected to be a dict with:
    - "name": file name
    - "path_relative_to_root": relative path of the file
    - "size_in_bytes": size of the file in bytes
    - "sha256": sha256 hash of the file
    """
    local_set  = {canon(d) for d in local}
    remote_set = {canon(d) for d in remote}

    return [l_item for l_item in remote if canon(l_item) not in local_set], \
           [r_item for r_item in local if canon(r_item) not in remote_set]

def write_public_index(remote_id: dict[str, str], local_manifest: list[dict]) -> None:
    """
    Create manifests/public_index.json that allows public (no-credentials) download after clone.

    Format (list):
      {
        "path_relative_to_root": "...",
        "sha256": "...",
        "size_in_bytes": 123,
        "drive_file_id": "...."
      }
    """
    out = []
    missing = []

    for it in local_manifest:
        p = it.get("path_relative_to_root")
        if not p:
            continue
        fid = remote_id.get(p)
        if not fid:
            missing.append(p)
            continue
        out.append({
            "path_relative_to_root": p,
            "sha256": it.get("sha256", ""),
            "size_in_bytes": int(it.get("size_in_bytes", 0) or 0),
            "drive_file_id": fid,
        })

    out_path = MANIFESTS_DIR / "public_index.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf8")

    if missing:
        print(f"WARNING: public_index missing {len(missing)} paths (no drive_file_id). Files missing:")
        for p in missing:
            print(f"  - {p}")
    print(f"Wrote public index -> {out_path}")

# Drive utils
_DRIVE_SERVICE = None
_FOLDER_IDS = None
_FOLDER_CACHE: dict[tuple[str, str], str] = {}  # (parent_id, folder_name) -> folder_id
PLAN_NAME = "last_sync_plan.json"

def _get_drive_service():
    """Authenticate and return a Google Drive service instance."""
    global _DRIVE_SERVICE
    if _DRIVE_SERVICE is not None:
        return _DRIVE_SERVICE

    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds_path = (CLOUD_DIR / "creds" / "credentials.json")
    token_path = (CLOUD_DIR / "creds" / "token.json")
    if not creds_path.exists():
        raise RuntimeError(f"Missing creds: {creds_path}")

    SCOPES = ["https://www.googleapis.com/auth/drive"]

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf8")

    _DRIVE_SERVICE = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _DRIVE_SERVICE

def _find_folder_id(service, name: str, parent_id: str | None = None) -> str | None:
    name_esc = name.replace("'", "\\'")
    q = (
        f"name = '{name_esc}' and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )
    if parent_id:
        q += f" and '{parent_id}' in parents"
    res = service.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def _get_folder_ids():
    global _FOLDER_IDS
    if _FOLDER_IDS is not None:
        return _FOLDER_IDS

    service = _get_drive_service()
    root_id = _find_folder_id(service, DRIVE_ROOT_FOLDER_NAME)
    if not root_id:
        raise RuntimeError(f"Drive root folder not found: {DRIVE_ROOT_FOLDER_NAME}")

    assets_id = _find_folder_id(service, DRIVE_ASSETS_FOLDER_NAME, parent_id=root_id)
    if not assets_id:
        raise RuntimeError(f"assets/ folder not found inside {DRIVE_ROOT_FOLDER_NAME}")

    archive_id = _find_folder_id(service, DRIVE_ARCHIVE_FOLDER_NAME, parent_id=root_id)
    if not archive_id:
        raise RuntimeError(f"archive/ folder not found inside {DRIVE_ROOT_FOLDER_NAME}")

    _FOLDER_IDS = (root_id, assets_id, archive_id)
    return _FOLDER_IDS

def build_remote_id_map() -> dict[str, str]:
    """Build a map from repo_path (relative path under assets/) to Drive file ID.    """
    service = _get_drive_service()
    _, assets_id, _ = _get_folder_ids()

    # 1) Zbierz wszystkie foldery i pliki pod assets/ (BFS, paginacja)
    folders: dict[str, tuple[str, str | None]] = {assets_id: ("", None)}  # id -> (name, parent_id)
    files: list[tuple[str, str, str]] = []  # (file_id, file_name, parent_folder_id)

    queue = [assets_id]
    seen = set(queue)

    while queue:
        parent = queue.pop()

        page_token = None
        while True:
            resp = service.files().list(
                q=f"'{parent}' in parents and trashed = false",
                fields="nextPageToken, files(id,name,mimeType,parents)",
                pageToken=page_token,
                pageSize=1000,
            ).execute()

            for it in resp.get("files", []):
                fid = it["id"]
                name = it.get("name", "")
                mime = it.get("mimeType", "")
                parents = it.get("parents") or []
                par = parents[0] if parents else None

                if mime == "application/vnd.google-apps.folder":
                    # folder
                    folders[fid] = (name, par)
                    if fid not in seen:
                        seen.add(fid)
                        queue.append(fid)
                else:
                    # file
                    if par:
                        files.append((fid, name, par))

            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    # 2) Zbuduj ścieżki folderów względne do assets/
    folder_path_cache: dict[str, str] = {}

    def folder_rel_path(folder_id: str) -> str:
        if folder_id in folder_path_cache:
            return folder_path_cache[folder_id]
        if folder_id == assets_id:
            folder_path_cache[folder_id] = ""
            return ""

        name, parent = folders.get(folder_id, ("", None))
        if not parent:
            # folder spoza drzewa assets (nie powinno się zdarzyć)
            folder_path_cache[folder_id] = name
            return name

        parent_rel = folder_rel_path(parent)
        rel = str(PurePosixPath(parent_rel) / name) if parent_rel else name
        folder_path_cache[folder_id] = rel
        return rel

    # 3) Mapuj pliki na repo_path
    out: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}

    for file_id, file_name, parent_id in files:
        rel_dir = folder_rel_path(parent_id)
        repo_path = str(PurePosixPath(rel_dir) / file_name) if rel_dir else file_name

        if repo_path in out:
            duplicates.setdefault(repo_path, [out[repo_path]]).append(file_id)
        else:
            out[repo_path] = file_id

    if duplicates:
        # Drive pozwala na duplikaty w tym samym folderze, więc MUSISZ to obsłużyć.
        # Na razie wywalamy błąd, żebyś nie archiwizował losowego pliku.
        msg = "Duplicate paths on Drive (same repo_path, multiple fileIds):\n"
        for p, ids in duplicates.items():
            msg += f"  - {p}: {ids}\n"
        raise RuntimeError(msg)

    return out

def _find_file_id_in_folder(service, parent_id: str, filename: str) -> str | None:
    name_esc = filename.replace("'", "\\'")
    q = f"'{parent_id}' in parents and name = '{name_esc}' and trashed = false"
    res = service.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def _find_file_ids_in_folder(service, parent_id: str, filename: str) -> list[str]:
    name_esc = filename.replace("'", "\\'")
    q = f"'{parent_id}' in parents and name = '{name_esc}' and trashed = false"
    res = service.files().list(q=q, fields="files(id,name)", pageSize=100).execute()
    return [f["id"] for f in res.get("files", [])]

def _ensure_folder(service, parent_id: str, name: str) -> str:
    key = (parent_id, name)
    if key in _FOLDER_CACHE:
        return _FOLDER_CACHE[key]

    # try find
    name_esc = name.replace("'", "\\'")
    q = (
        f"'{parent_id}' in parents and name = '{name_esc}' "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    res = service.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = res.get("files", [])
    if files:
        fid = files[0]["id"]
        _FOLDER_CACHE[key] = fid
        return fid

    # create
    created = service.files().create(
        body={
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        },
        fields="id",
    ).execute()
    fid = created["id"]
    _FOLDER_CACHE[key] = fid
    return fid

def _assets_parent_for_repo_path(repo_path: str) -> str:
    """
    repo_path np. "Assets/Renderers/a.png" corresponds to Drive path "assets/Renderers/a.png" (relative to root).
    This function ensures the folder structure exists in Drive and returns the parent folder ID for the file
    """
    service = _get_drive_service()
    _, assets_id, _ = _get_folder_ids()

    parts = Path(repo_path).parts
    if len(parts) <= 1:
        return assets_id

    folder_parts = parts[:-1]

    cur = assets_id
    for folder in folder_parts:
        cur = _ensure_folder(service, cur, folder)
    return cur

# Drive operations
def move_remote_to_archive(drive_id: str) -> None:
    """Move a remote file to the archive folder."""
    service = _get_drive_service()
    _, _, archive_id = _get_folder_ids()

    meta = service.files().get(fileId=drive_id, fields="parents").execute()
    parents = meta.get("parents") or []
    if not parents:
        raise RuntimeError(f"Remote file has no parents? id={drive_id}")

    service.files().update(
        fileId=drive_id,
        addParents=archive_id,
        removeParents=",".join(parents),
        fields="id, parents",
    ).execute()

def upload_local(repo_path: str) -> None:
    """Upload a local file to the correct location in Drive (under assets/)."""
    service = _get_drive_service()

    local_path = REPO_ROOT / repo_path
    if not local_path.exists():
        raise RuntimeError(f"Local file missing: {local_path}")

    parent_id = _assets_parent_for_repo_path(repo_path)

    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(local_path), resumable=True)

    body = {
        "name": local_path.name,
        "parents": [parent_id],
    }
    
    return service.files().create(body=body, media_body=media, fields="id").execute()["id"]

def replace_remote_with_local(repo_path: str) -> None:
    """Upload local file as replacement (after remote archived)."""
    upload_local(repo_path)

def upload_sync_plan(
    to_archive: list[str],
    to_upload: list[str]
) -> None:
    """
    Upload a sync plan to Drive root as last_sync_plan.json.
    This is an audit/recovery; it does NOT represent final state.
    """
    service = _get_drive_service()
    root_id, _, _ = _get_folder_ids()

    plan = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "archive": to_archive,
        "upload_new": to_upload,
    }

    tmp_id = _find_file_id_in_folder(service, root_id, PLAN_NAME)

    payload = json.dumps(plan, indent=2, ensure_ascii=False).encode("utf8")
    media = MediaInMemoryUpload(payload, mimetype="application/json", resumable=False)

    if tmp_id:
        service.files().update(fileId=tmp_id, media_body=media).execute()
    else:
        service.files().create(
            body={"name": PLAN_NAME, "parents": [root_id]},
            media_body=media,
            fields="id",
        ).execute()

def update_remote_manifest() -> None:
    """Upsert remote_manifest.json in Drive root (no duplicates)."""
    service = _get_drive_service()
    root_id, _, _ = _get_folder_ids()

    media = MediaFileUpload(
        str(LOCAL_MANIFEST_PATH),
        mimetype="application/json",
        resumable=False,
    )

    ids = _find_file_ids_in_folder(service, root_id, DRIVE_MANIFEST_FILENAME)

    if ids:
        # keep the first, delete the rest (cleanup duplicates)
        keep = ids[0]
        for dup in ids[1:]:
            service.files().delete(fileId=dup).execute()

        service.files().update(
            fileId=keep,
            media_body=media,
        ).execute()
    else:
        service.files().create(
            body={"name": DRIVE_MANIFEST_FILENAME, "parents": [root_id]},
            media_body=media,
            fields="id",
        ).execute()

# Main
def main() -> int:

    print("\nPreparing sync...")
    # Load manifests
    local = load_json_list(LOCAL_MANIFEST_PATH)
    remote = load_json_list(REMOTE_INDEX_PATH)
    remote_id = build_remote_id_map()

    # Plan actions and apply in safe order
    to_archive, to_upload = plan(local, remote)
    if not (to_archive or to_upload):
        print("Already in sync.")
    
    else:
        # Upload the plan
        print("\nUploading sync plan to Drive...\n")
        upload_sync_plan(to_archive, to_upload)

        # Apply the plan
        if to_archive:
            arch_len = len(to_archive)
            print(f"Will archive {len(to_archive)} remote paths")
            for i, p in enumerate(to_archive, start=1):
                tmp_path = p.get("path_relative_to_root", "<missing_path>")
                print(f"  {i}/{arch_len} - {('...' if len(tmp_path) > 60 else '')}{tmp_path[len(tmp_path)-60:] if len(tmp_path) > 60 else tmp_path}")
                move_remote_to_archive(remote_id[tmp_path])
                remote_id.pop(tmp_path, None)  # Remove archived from remote_id map, so they won't be included in public index

        if to_upload:
            upl_len = len(to_upload)
            print(f"Will upload {len(to_upload)} new paths")
            for i, p in enumerate(to_upload, start=1):
                tmp_path = p.get("path_relative_to_root", "<missing_path>")
                print(f"  {i}/{upl_len} - {('...' if len(tmp_path) > 60 else '')}{tmp_path[len(tmp_path)-60:] if len(tmp_path) > 60 else tmp_path}")
                fid = upload_local(tmp_path)
                remote_id[tmp_path] = fid  # Update the remote_id map for new uploads, so public index can be generated correctly

    print("\nUpdating remote manifest...")
    update_remote_manifest()

    print("Writing public index...")
    write_public_index(remote_id, local)

    print("Appending to log...")
    append_cloud_sync_log(
        upload_count=len(to_upload),
        archive_count=len(to_archive),
        local_manifest=Path("Src/Cloud/manifests/local_manifest.json"),
        remote_manifest=Path("Src/Cloud/manifests/remote_manifest.json"),
    )

    return 0

# Entry point
if __name__ == "__main__":
    raise SystemExit(main()) # Return code from main()
