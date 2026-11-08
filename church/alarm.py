import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from telegram import Bot
from config import get_bool, get_env
from logger import error_logger, status_logger


@dataclass
class TGAlarm:
    bot_token: str
    chat_id: int

    def __post_init__(self):
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
        else:
            self.bot = None

    def alarm(self, message: str, ex: Exception | None = None) -> None:
        async def _send():
            text = f"🚨 ALARM\n{message}"
            if ex:
                text += f"\n{type(ex).__name__}: {ex}"

            try:
                if ex:
                    error_logger.error(message, exc_info=ex)
                else:
                    status_logger.warning(message)

                if use_stdout or not self.bot or not self.chat_id:
                    status_logger.warning(text)
                    return

                await self.bot.send_message(chat_id=self.chat_id, text=text)
            except Exception as e:
                error_logger.error(e)

        try:
            asyncio.run(_send())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.create_task(_send())

    def recovery(self, message: str) -> None:
        """Send a single successful-recovery notification."""
        async def _send():
            text = f"✅ RECOVERED\n{message}"
            try:
                status_logger.info(message)
                if use_stdout or not self.bot or not self.chat_id:
                    status_logger.info(text)
                    return
                await self.bot.send_message(chat_id=self.chat_id, text=text)
            except Exception as e:
                error_logger.error(e)

        try:
            asyncio.run(_send())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.create_task(_send())


@dataclass
class PersistentAlarm:
    """Suppress repeated alerts for the same incident across process restarts."""

    alarm_client: TGAlarm
    state_path: Path

    def report_once(self, key: str, message: str, ex: Exception) -> bool:
        """Report a new failure and return whether a Telegram alert was sent."""
        fingerprint = f"{type(ex).__name__}: {ex}"
        state = self._load()
        incidents = state.setdefault("incidents", {})
        incident = incidents.get(key)
        now = datetime.now(timezone.utc).isoformat()

        if incident and incident.get("fingerprint") == fingerprint:
            incident["last_seen"] = now
            self._save(state)
            error_logger.error("Suppressed duplicate alarm for %s: %s", key, fingerprint)
            return False

        incidents[key] = {
            "fingerprint": fingerprint,
            "first_seen": now,
            "last_seen": now,
        }
        self._save(state)
        self.alarm_client.alarm(message, ex)
        return True

    def resolve(self, key: str, message: str) -> bool:
        """Close an active incident and announce recovery once."""
        state = self._load()
        incidents = state.setdefault("incidents", {})
        if key not in incidents:
            return False

        del incidents[key]
        self._save(state)
        self.alarm_client.recovery(message)
        return True

    def _load(self) -> dict:
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except (OSError, json.JSONDecodeError) as exc:
            error_logger.error("Unable to read alarm state %s: %s", self.state_path, exc)
            return {}

    def _save(self, state: dict) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.state_path.with_suffix(f"{self.state_path.suffix}.tmp")
        temporary_path.write_text(
            json.dumps(state, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        temporary_path.replace(self.state_path)


use_stdout = get_bool("ALARM_STDOUT")
bot_token = get_env("BOT_TOKEN") or ""
chat_id_raw = get_env("CHAT_ID") or ""
chat_id = int(chat_id_raw) if chat_id_raw.isdigit() else 0

tg_alarm = TGAlarm(bot_token=bot_token, chat_id=chat_id)
