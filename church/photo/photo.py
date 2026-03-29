import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

project_path = Path(__file__).resolve()
for root in (project_path.parents[1], project_path.parents[2]):
	if str(root) not in sys.path:
		sys.path.insert(0, str(root))

from alarm import tg_alarm
from db import get_category_folders, save_drive_uploads_for_folder
from drive_client import get_drive_service
from logger import status_logger


def _build_list_kwargs(query: str, page_token: str | None = None) -> Dict[str, object]:
	list_kwargs: Dict[str, object] = {
		"q": query,
		"spaces": "drive",
		"fields": "nextPageToken, files(id,name,mimeType,createdTime,modifiedTime)",
		"supportsAllDrives": True,
		"includeItemsFromAllDrives": True,
		"pageSize": 1000,
	}
	if page_token:
		list_kwargs["pageToken"] = page_token

	shared_drive_id = (os.getenv("DRIVE_SHARED_DRIVE_ID") or "").strip()
	if shared_drive_id:
		list_kwargs["driveId"] = shared_drive_id
		list_kwargs["corpora"] = "drive"
	return list_kwargs


def list_drive_images_for_folder(drive_service, folder_id: str) -> List[Dict[str, str]]:
	query = f"'{folder_id}' in parents and trashed=false"
	page_token = None
	uploads: List[Dict[str, str]] = []

	while True:
		list_kwargs = _build_list_kwargs(query, page_token)
		response = drive_service.files().list(**list_kwargs).execute()
		for file_obj in response.get("files", []):
			mime_type = str(file_obj.get("mimeType") or "").lower()
			if not mime_type.startswith("image/"):
				continue

			drive_file_id = str(file_obj.get("id") or "").strip()
			if not drive_file_id:
				continue

			drive_date = (
				file_obj.get("createdTime")
				or file_obj.get("modifiedTime")
				or datetime.now(timezone.utc).date().isoformat()
			)
			uploads.append(
				{
					"drive_file_id": drive_file_id,
					"drive_date": str(drive_date),
				}
			)

		page_token = response.get("nextPageToken")
		if not page_token:
			break

	return uploads


def sync_folder_to_db(drive_service, folder_id: str, folder_name: str) -> None:
	uploads = list_drive_images_for_folder(drive_service, folder_id)
	stats = save_drive_uploads_for_folder(folder_id, uploads)
	status_logger.info(
		"Drive->DB sync for '%s' (%s): files=%s created=%s updated=%s deleted=%s",
		folder_name,
		folder_id,
		len(uploads),
		stats.get("created", 0),
		stats.get("updated", 0),
		stats.get("deleted", 0),
	)


def main() -> None:
	status_logger.info("Drive sync started")
	folders = get_category_folders()
	if not folders:
		status_logger.info("No category folders found in DB")
		return

	drive_service = get_drive_service()
	for folder in folders:
		folder_id = folder["id"]
		folder_name = folder["name"]
		try:
			sync_folder_to_db(drive_service, folder_id, folder_name)
		except Exception as folder_error:
			tg_alarm.alarm(f"Drive sync failed for folder '{folder_name}' ({folder_id}):", folder_error)

	status_logger.info("Drive sync finished")


if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		tg_alarm.alarm("Drive sync failed", e)
		raise
