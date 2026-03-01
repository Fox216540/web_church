import logging
import sys
from logging import Formatter
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = Path("./logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


class Configs:

	@staticmethod
	def _file_handler(file_name: str, level: int):
		handler = RotatingFileHandler(
			filename=LOG_DIR / file_name,
			maxBytes=2 ** 20,  # 1 MB
			backupCount=2,  # log, log.1, log.2 (максимум 3 файла)
			encoding="utf-8"
		)
		handler.setFormatter(Formatter(LOG_FORMAT))
		handler.setLevel(level)
		return handler

	@staticmethod
	def status_logger(name: str = "status"):
		log = logging.getLogger(name)
		log.setLevel(logging.INFO)
		log.propagate = False

		if not log.handlers:
			# файл
			log.addHandler(Configs._file_handler("status.log", logging.INFO))

			# терминал
			console = logging.StreamHandler(sys.stdout)
			console.setFormatter(Formatter(LOG_FORMAT))
			console.setLevel(logging.INFO)
			log.addHandler(console)

		return log

	@staticmethod
	def error_logger(name: str = "error"):
		log = logging.getLogger(name)
		log.setLevel(logging.ERROR)
		log.propagate = False

		if not log.handlers:
			handler = RotatingFileHandler(
				filename=LOG_DIR / "error.log",
				maxBytes=5 * 1024 * 1024,  # 5 MB
				backupCount=3,
				encoding="utf-8"
			)
			handler.setFormatter(Formatter(LOG_FORMAT))
			handler.setLevel(logging.ERROR)
			log.addHandler(handler)

		return log

	@staticmethod
	def get_status_logger(name: str):
		safe_name = name.replace(".", "_")
		log = logging.getLogger(name)
		log.setLevel(logging.INFO)
		log.propagate = False

		if not log.handlers:
			log.addHandler(Configs._file_handler(f"{safe_name}.log", logging.INFO))

			console = logging.StreamHandler(sys.stdout)
			console.setFormatter(Formatter(LOG_FORMAT))
			console.setLevel(logging.INFO)
			log.addHandler(console)

		return log

	@staticmethod
	def get_error_logger(name: str):
		safe_name = name.replace(".", "_")
		log = logging.getLogger(f"{name}.error")
		log.setLevel(logging.ERROR)
		log.propagate = False

		if not log.handlers:
			handler = RotatingFileHandler(
				filename=LOG_DIR / f"{safe_name}_error.log",
				maxBytes=5 * 1024 * 1024,
				backupCount=3,
				encoding="utf-8"
			)
			handler.setFormatter(Formatter(LOG_FORMAT))
			handler.setLevel(logging.ERROR)
			log.addHandler(handler)

		return log

status_logger = Configs.status_logger()
error_logger = Configs.error_logger()

