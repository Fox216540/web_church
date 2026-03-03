import os
import pickle
import sys
from datetime import datetime
from pathlib import Path

from typing import Dict, List

project_path = Path(__file__).resolve()
for root in (project_path.parents[1], project_path.parents[2]):
	if str(root) not in sys.path:
		sys.path.insert(0, str(root))

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateutil.parser import parse
from db import get_category_folders, save_photos_for_folder
from alarm import tg_alarm

from logger import status_logger

class GoogleDriveMultiTracker:
	"""
	Класс для отслеживания изменений в нескольких папках Google Диска
	с генерацией ссылок на файлы
	"""
	SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
	STATE_FILE = 'photo/auth/drive_multi_state.pkl'

	def __init__(self, folder_ids: List[str], credentials_file: str = 'photo/auth/credentials.json'):
		self.folder_ids = folder_ids
		self.credentials_file = credentials_file
		self.service = None
		self.state = self._load_state()

	def _load_state(self) -> Dict:
		"""Загружает предыдущее состояние для всех папок"""
		if os.path.exists(self.STATE_FILE):
			with open(self.STATE_FILE, 'rb') as f:
				return pickle.load(f)
		return {
			'last_check': datetime.min,
			'folders': {fid: {'known_files': {}} for fid in self.folder_ids}}

	def _save_state(self):
		"""Сохраняет текущее состояние проверок"""
		with open(self.STATE_FILE, 'wb') as f:
			pickle.dump(self.state, f)

	def authenticate(self):
		"""Аутентификация в Google Drive API"""
		creds = None
		token_file = 'photo/auth/drive_multi_token.pickle'

		if os.path.exists(token_file):
			with open(token_file, 'rb') as token:
				creds = pickle.load(token)

		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					self.credentials_file, self.SCOPES)
				creds = flow.run_local_server(port=0)

			with open(token_file, 'wb') as token:
				pickle.dump(creds, token)

		self.service = build('drive', 'v3', credentials=creds)

	def _build_query(self) -> str:
		"""Строит комбинированный запрос для всех папок"""
		folders_query = ' or '.join([f"'{fid}' in parents" for fid in self.folder_ids])
		return f"({folders_query}) and trashed = false and mimeType contains 'image/'"

	def _get_file_links(self, file_id: str) -> Dict:
		"""Получает прямые ссылки на файл"""
		file = self.service.files().get(
			fileId=file_id,
			fields="webViewLink, webContentLink"
		).execute()
		return {
			'view': file.get('webViewLink'),
			'download': file.get('webContentLink')
		}

	def _get_all_files(self) -> Dict[str, Dict]:
		"""Получает все файлы из отслеживаемых папок"""
		all_files = {}
		page_token = None
		query = self._build_query()

		while True:
			response = self.service.files().list(
				q=query,
				fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, parents)",
				pageToken=page_token,
				pageSize=1000
			).execute()

			for file in response.get('files', []):
				file_id = file['id']
				file['links'] = self._get_file_links(file_id)
				file['parent_folders'] = [p for p in file.get('parents', []) if p in self.folder_ids]
				all_files[file_id] = file

			page_token = response.get('nextPageToken')
			if not page_token:
				break

		return all_files

	def check_changes(self) -> Dict[str, Dict]:
		"""
		Возвращает изменения по всем папкам со ссылками:
		{
			'folder_id1': {
				'new_files': [{'name': ..., 'links': ...}, ...],
				'updated_files': [...],
				'removed_files': [...]
			},
			...
		}
		"""
		if not self.service:
			raise RuntimeError("Сначала выполните аутентификацию!")

		current_files = self._get_all_files()
		changes = {fid: {'new_files': [], 'updated_files': [], 'removed_files': []} for fid in self.folder_ids}

		for folder_id in self.folder_ids:
			prev_files = self.state['folders'][folder_id]['known_files']
			curr_folder_files = {fid: f for fid, f in current_files.items()
			                     if folder_id in f.get('parent_folders', [])}

			# Новые файлы
			changes[folder_id]['new_files'] = [
				{
					'name': f['name'],
					'links': f['links'],
					'id': f['id']
				} for fid, f in curr_folder_files.items() if fid not in prev_files
			]

			# Обновленные файлы
			changes[folder_id]['updated_files'] = [
				{
					'name': f['name'],
					'links': f['links'],
					'id': f['id']
				} for fid, f in curr_folder_files.items()
				if fid in prev_files and parse(f['modifiedTime']) > parse(prev_files[fid]['modifiedTime'])
			]

			# Удаленные файлы
			changes[folder_id]['removed_files'] = [
				{
					'name': f['name'],
					'id': fid
				} for fid, f in prev_files.items() if fid not in curr_folder_files
			]

		# Обновляем состояние
		self.state['last_check'] = datetime.now()
		now_iso = datetime.now().isoformat()
		for folder_id in self.folder_ids:
			prev_folder_files = self.state['folders'][folder_id]['known_files']
			self.state['folders'][folder_id]['known_files'] = {
				fid: {
					**f,
					'first_seen_in_folder': (
						prev_folder_files[fid].get('first_seen_in_folder')
						if fid in prev_folder_files
						else now_iso
					)
				}
				for fid, f in current_files.items()
				if folder_id in f.get('parent_folders', [])
			}
		self._save_state()

		return changes

	def get_current_photo_summary(self) -> Dict[str, List[Dict[str, str]]]:
		"""Возвращает актуальные фото по папкам: id + даты."""
		result = {}
		for folder_id in self.folder_ids:
			known_files = self.state['folders'].get(folder_id, {}).get('known_files', {})
			items = []
			for fid, meta in known_files.items():
				items.append({
					'id': fid,
					'created_time': meta.get('createdTime', ''),
					'modified_time': meta.get('modifiedTime', ''),
					'first_seen_in_folder': meta.get('first_seen_in_folder', '')
				})
			result[folder_id] = sorted(items, key=lambda x: x['id'])
		return result


def main():
	status_logger.info("Photo sync started")
	folders = get_category_folders()
	if not folders:
		status_logger.info("No category folders found in DB")
		return
	folder_ids = [folder["id"] for folder in folders]
	folder_names = {folder["id"]: folder["name"] for folder in folders}
	status_logger.info("Loaded %s folder(s) from DB", len(folder_ids))
	run_tracker(folder_ids, folder_names)


def has_any_changes(changes: Dict[str, Dict]) -> bool:
	return any(
		folder_changes.get('new_files')
		or folder_changes.get('updated_files')
		or folder_changes.get('removed_files')
		for folder_changes in changes.values()
	)


def resolve_display_date(item: Dict[str, str]) -> str:
	created_time = item.get('created_time', '')
	first_seen = item.get('first_seen_in_folder', '')
	date_to_show = created_time

	if created_time and first_seen:
		created_dt = parse(created_time).replace(microsecond=0)
		first_seen_dt = parse(first_seen).replace(microsecond=0)
		if created_dt != first_seen_dt:
			date_to_show = first_seen
	elif first_seen:
		date_to_show = first_seen

	if not date_to_show:
		return ""
	return parse(date_to_show).strftime("%d.%m.%Y")



def run_tracker(folder_ids: List[str], folder_names: Dict[str, str]):
	tracker = GoogleDriveMultiTracker(folder_ids)
	try:
		status_logger.info("Authenticating Google Drive client")
		tracker.authenticate()
		status_logger.info("Checking changes in Google Drive")
		changes = tracker.check_changes()
		current_items = tracker.get_current_photo_summary()
		status_logger.info("Fetched current photo summary for %s folder(s)", len(current_items))
		sync_photos_to_db(current_items, folder_names)
		status_logger.info("Photo sync finished successfully")
	except Exception as e:
		tg_alarm.alarm("Photo sync failed", e)


def sync_photos_to_db(current_items: Dict[str, List[Dict[str, str]]], folder_names: Dict[str, str]):
	for folder_id, items in current_items.items():
		folder_name = folder_names.get(folder_id, folder_id)
		try:
			stats = save_photos_for_folder(folder_id, items)
			status_logger.info(
				"DB sync for folder '%s' (%s): created=%s updated=%s deleted=%s",
				folder_name,
				folder_id,
				stats["created"],
				stats["updated"],
				stats["deleted"],
			)
		except Exception as e:
			tg_alarm.alarm(
				f"DB sync failed for folder '{folder_name}' ({folder_id}):",
				e
			)


if __name__ == '__main__':
	main()

