import asyncio
import os
from dataclasses import dataclass

from telegram import Bot
from logger import error_logger


@dataclass
class TGAlarm:
    bot_token: str
    chat_id: int

    def __post_init__(self):
        self.bot = Bot(token=self.bot_token)

    def alarm(self, message: str, ex: Exception | None = None) -> None:
        async def _send():
            text = f"🚨 ALARM\n{message}"
            if ex:
                text += f"\n{type(ex).__name__}: {ex}"

            try:
                if ex:
                    error_logger.error(message, exc_info=ex)

                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text
                )
            except Exception as e:
                error_logger.error(e)

        try:
            asyncio.run(_send())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.create_task(_send())


chat_id = int(os.environ["CHAT_ID"])
bot_token = os.environ["BOT_TOKEN"]

tg_alarm = TGAlarm(bot_token=bot_token, chat_id=chat_id)