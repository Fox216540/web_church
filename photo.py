import os
import pickle
from datetime import datetime
from typing import Dict, List
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateutil.parser import parse


class GoogleDriveMultiTracker:
	"""
	Класс для отслеживания изменений в нескольких папках Google Диска
	с генерацией ссылок на файлы
	"""
	SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
	STATE_FILE = 'drive_multi_state.pkl'

	def __init__(self, folder_ids: List[str], credentials_file: str = 'credentials.json'):
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
		token_file = 'drive_multi_token.pickle'

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
				fields="nextPageToken, files(id, name, mimeType, modifiedTime, parents)",
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
		for folder_id in self.folder_ids:
			self.state['folders'][folder_id]['known_files'] = {
				fid: f for fid, f in current_files.items()
				if folder_id in f.get('parent_folders', [])
			}
		self._save_state()

		return changes


def main():
	FOLDER_IDS = [""]

	tracker = GoogleDriveMultiTracker(FOLDER_IDS)

	try:
		tracker.authenticate()
		changes = tracker.check_changes()

		for folder_id, folder_changes in changes.items():
			if any(folder_changes.values()):
				print(f"\nИзменения в папке {folder_id}:")

				if folder_changes['new_files']:
					for f in folder_changes['new_files']:
						return f['id'], f['name'], f['links']['view']

				if folder_changes['updated_files']:
					for f in folder_changes['updated_files']:
						return f['id'], f['name'], f['links']['view']

				if folder_changes['removed_files']:
					for f in folder_changes['removed_files']:
						return {f['id']}

			else:
				return None

	except Exception as e:
		print(f"Ошибка: {str(e)}")


if __name__ == '__main__':
	changed = main()
	if not changed:
		print(f"\nВ папках изменений нет.")
	else:
		print(changed)