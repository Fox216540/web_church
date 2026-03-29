import asyncio
import os
from dataclasses import dataclass

from telegram import Bot
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


use_stdout = (os.getenv("ALARM_STDOUT") or "").lower() in {"1", "true", "yes"}
bot_token = os.getenv("BOT_TOKEN") or ""
chat_id_raw = os.getenv("CHAT_ID") or ""
chat_id = int(chat_id_raw) if chat_id_raw.isdigit() else 0

tg_alarm = TGAlarm(bot_token=bot_token, chat_id=chat_id)
