import pickle
from functools import lru_cache
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/drive"]
AUTH_DIR = Path(__file__).resolve().parent / "auth"
TOKEN_FILE = AUTH_DIR / "drive_token.pickle"
CREDENTIALS_FILE = AUTH_DIR / "credentials.json"


@lru_cache(maxsize=1)
def get_drive_service():
	"""
	Authenticate and return Google Drive API client.
	"""
	creds = None
	if TOKEN_FILE.exists():
		with TOKEN_FILE.open("rb") as token:
			creds = pickle.load(token)

	if not creds or not creds.valid or (creds and hasattr(creds, "has_scopes") and not creds.has_scopes(SCOPES)):
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			if not CREDENTIALS_FILE.exists():
				raise FileNotFoundError(f"Missing credentials file: {CREDENTIALS_FILE}")
			flow = InstalledAppFlow.from_client_secrets_file(
				str(CREDENTIALS_FILE),
				SCOPES,
			)
			creds = flow.run_local_server(port=0)

		AUTH_DIR.mkdir(parents=True, exist_ok=True)
		with TOKEN_FILE.open("wb") as token:
			pickle.dump(creds, token)

	return build("drive", "v3", credentials=creds)
