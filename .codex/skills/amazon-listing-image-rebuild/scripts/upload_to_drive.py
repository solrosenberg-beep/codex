#!/usr/bin/env python3
"""Upload a finished image set to the Sound Around image shared drive.

Creates (or reuses) a folder named <SKU>-CODEX at the root of the shared drive
and uploads every file in the given folder into it, in filename order.

Usage:
    python upload_to_drive.py --sku PKDRM8 --folder work/B0XXXXXXX/new

Auth (one time, done by Sol or IT):
    1. Create a Google Cloud service account and download its JSON key.
    2. Share the image shared drive with the service account email (Content manager).
    3. Put the JSON in the environment as GDRIVE_SERVICE_ACCOUNT_JSON
       (the full JSON text) or GDRIVE_SERVICE_ACCOUNT_FILE (a path to the file).
       In web Codex: project settings, Environment, Secrets.

Dependencies: pip install google-api-python-client google-auth
"""
import argparse
import json
import mimetypes
import os
import sys
from pathlib import Path

SHARED_DRIVE_ID = "0AJnODehJPHg5Uk9PVA"  # Sound Around image drive root (SKU folders live here)
SUFFIX = "-CODEX"


def get_service():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("Run: pip install google-api-python-client google-auth")

    scopes = ["https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON")
    path = os.environ.get("GDRIVE_SERVICE_ACCOUNT_FILE")
    if raw:
        creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=scopes)
    elif path:
        creds = service_account.Credentials.from_service_account_file(path, scopes=scopes)
    else:
        sys.exit(
            "No Google Drive credentials. Set GDRIVE_SERVICE_ACCOUNT_JSON or "
            "GDRIVE_SERVICE_ACCOUNT_FILE. See the docstring at the top of this script."
        )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def find_or_create_folder(svc, name, parent_id):
    q = (
        f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed = false"
    )
    res = svc.files().list(
        q=q, spaces="drive", fields="files(id, name)",
        supportsAllDrives=True, includeItemsFromAllDrives=True,
        corpora="drive", driveId=SHARED_DRIVE_ID,
    ).execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"], False
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
    f = svc.files().create(body=meta, fields="id", supportsAllDrives=True).execute()
    return f["id"], True


def upload_file(svc, path: Path, parent_id: str):
    from googleapiclient.http import MediaFileUpload

    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    media = MediaFileUpload(str(path), mimetype=mime, resumable=False)
    meta = {"name": path.name, "parents": [parent_id]}
    f = svc.files().create(body=meta, media_body=media, fields="id, name", supportsAllDrives=True).execute()
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sku", required=True, help="Sound Around SKU, e.g. PKDRM8")
    ap.add_argument("--folder", required=True, help="Local folder holding the finished images")
    ap.add_argument("--parent", default=SHARED_DRIVE_ID, help="Drive folder id to create the SKU folder in")
    ap.add_argument("--include-thumbs", action="store_true", help="Also upload *.thumb.png check files")
    args = ap.parse_args()

    src = Path(args.folder)
    if not src.is_dir():
        sys.exit(f"Folder not found: {src}")

    files = sorted(p for p in src.iterdir() if p.is_file() and not p.name.startswith("."))
    if not args.include_thumbs:
        files = [p for p in files if ".thumb." not in p.name]
    if not files:
        sys.exit(f"No files to upload in {src}")

    svc = get_service()
    folder_name = f"{args.sku.strip().upper()}{SUFFIX}"
    folder_id, created = find_or_create_folder(svc, folder_name, args.parent)
    print(f"{'Created' if created else 'Using existing'} folder {folder_name} ({folder_id})")

    for p in files:
        f = upload_file(svc, p, folder_id)
        print(f"  uploaded {f['name']}")

    print(f"\nDone. {len(files)} files in https://drive.google.com/drive/folders/{folder_id}")


if __name__ == "__main__":
    main()
