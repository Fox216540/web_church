# Скрипт: Загрузка видео на YouTube через Python (ООП)
# Требования:
# 1. Создать проект в Google Cloud Console и включить YouTube Data API v3
# 2. Создать OAuth 2.0 Client ID (Application type: Desktop)
# 3. Сохранить credentials.json в папку с этим скриптом
# 4. Установить зависимости:
#    pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

class YouTubeUploader:
    """
    Класс для загрузки видео на YouTube через API v3.
    """
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'

    def __init__(self,
                 client_secrets_file: str = 'credentials.json',
                 scopes=None):
        if scopes is None:
            scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.client_secrets_file = client_secrets_file
        self.scopes = scopes
        self.credentials = None
        self.youtube = None

    def authenticate(self):
        """
        Авторизация OAuth2 и создание сервиса YouTube.
        """
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token_file:
                self.credentials = pickle.load(token_file)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    print("Токен обновлён автоматически.")
                except Exception as e:
                    print(f"Не удалось обновить токен: {e}\nЗапуск авторизации заново...")
                    self._manual_auth()
            else:
                self._manual_auth()

            with open('token.pickle', 'wb') as token_file:
                pickle.dump(self.credentials, token_file)

        self.youtube = build(
            self.API_SERVICE_NAME,
            self.API_VERSION,
            credentials=self.credentials
        )

    def _manual_auth(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes)
        self.credentials = flow.run_local_server(port=0)

    def upload_video(self,
                     video_file: str,
                     title: str,
                     description: str,
                     tags: list = None,
                     category_id: str = '22',
                     privacy_status: str = 'private') -> str:
        """
        Загружает видео и возвращает URL загруженного ролика.
        """
        if self.youtube is None:
            raise RuntimeError('Сервис не инициализирован. Вызовите authenticate().')

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
        request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        print('Начинаем загрузку...')
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f'Загружено {int(status.progress() * 100)}%')

        video_id = response.get('id')
        video_url = f'https://youtu.be/{video_id}'
        print(f'Загрузка завершена. Ссылка: {video_url}')
        return video_url


def main():
    uploader = YouTubeUploader()
    try:
        uploader.authenticate()
        url = uploader.upload_video(
            video_file='video.mp4',
            title='Заголовок видео',
            description='Описание видео',
            tags=['python', 'youtube', 'api'],
            category_id='22',  # People & Blogs
            privacy_status='public'
        )
        print(f'Видео доступно по ссылке: {url}')
    except HttpError as e:
        print(f'Произошла ошибка HTTP: {e.resp.status} - {e.content}')
    except Exception as ex:
        print(f'Ошибка: {ex}')

if __name__ == '__main__':
    main()
