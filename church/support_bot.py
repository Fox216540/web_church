import asyncio
import os
from dataclasses import dataclass, field
import json
from pathlib import Path
import re

from dotenv import load_dotenv
from telegram import Message, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from logger import error_logger, status_logger

load_dotenv()


@dataclass
class SupportState:
    admin_chat_id: int
    # user_chat_id -> last_admin_message_id
    user_last_ticket: dict[int, int] = field(default_factory=dict)
    storage_path: Path = Path("state/support_bot_state.json")

    def load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except Exception:
            return

        data = raw.get("user_last_ticket", {})
        loaded: dict[int, int] = {}
        for k, v in data.items():
            try:
                loaded[int(k)] = int(v)
            except (TypeError, ValueError):
                continue
        self.user_last_ticket = loaded

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "user_last_ticket": {str(k): v for k, v in self.user_last_ticket.items()}
        }
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _format_user(update: Update) -> str:
    user = update.effective_user
    if not user:
        return "unknown"

    parts = [f"id={user.id}"]
    if user.username:
        parts.append(f"@{user.username}")
    full_name = " ".join(p for p in [user.first_name, user.last_name] if p).strip()
    if full_name:
        parts.append(full_name)
    return ", ".join(parts)


def _ticket_text(update: Update, body: str) -> str:
    return (
        f"Новое обращение\n"
        f"Пользователь: {_format_user(update)}\n\n"
        f"{body}"
    )


def _extract_user_id_from_ticket(message: Message) -> int | None:
    source = message.text or message.caption or ""
    uid_match = re.search(r"\bUID:(\d+)\b", source)
    if uid_match:
        return int(uid_match.group(1))

    # Fallback for old format tickets where only "id=..." existed.
    legacy_match = re.search(r"\bid=(\d+)\b", source)
    if legacy_match:
        return int(legacy_match.group(1))

    return None


async def _send_ticket_to_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    state: SupportState,
    text: str,
    photo_file_id: str | None = None,
    reply_to_admin_message_id: int | None = None,
) -> Message:
    ticket_text = _ticket_text(update, text)
    try:
        if photo_file_id:
            sent = await context.bot.send_photo(
                chat_id=state.admin_chat_id,
                photo=photo_file_id,
                caption=ticket_text,
                reply_to_message_id=reply_to_admin_message_id,
            )
        else:
            sent = await context.bot.send_message(
                chat_id=state.admin_chat_id,
                text=ticket_text,
                reply_to_message_id=reply_to_admin_message_id,
            )
    except BadRequest as ex:
        err = str(ex).lower()
        reply_not_found = (
            "reply message not found" in err
            or "message to be replied not found" in err
        )
        if reply_to_admin_message_id and reply_not_found:
            if photo_file_id:
                sent = await context.bot.send_photo(
                    chat_id=state.admin_chat_id,
                    photo=photo_file_id,
                    caption=ticket_text,
                )
            else:
                sent = await context.bot.send_message(
                    chat_id=state.admin_chat_id,
                    text=ticket_text,
                )
        else:
            raise

    user_chat_id = update.effective_chat.id
    state.user_last_ticket[user_chat_id] = sent.message_id
    state.save()
    return sent


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Напишите ваше сообщение в поддержку.\n"
        "После этого можно дополнительно отправить фотографию."
    )


async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state: SupportState = context.application.bot_data["support_state"]
    message = update.message
    text = (message.text or "").strip()
    if not text:
        return

    reply_to = state.user_last_ticket.get(update.effective_chat.id)
    await _send_ticket_to_admin(
        update,
        context,
        state,
        text=text,
        reply_to_admin_message_id=reply_to,
    )
    await message.reply_text(
        "Спасибо за обращение. Техподдержка церковного сайта ответит вам в ближайшее время."
    )


async def handle_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state: SupportState = context.application.bot_data["support_state"]
    message = update.message
    photos = message.photo or []
    if not photos:
        return

    photo = photos[-1]
    caption = (message.caption or "").strip()
    if caption:
        text = caption
    else:
        text = "Фото к последнему обращению"
    reply_to = state.user_last_ticket.get(update.effective_chat.id)

    await _send_ticket_to_admin(
        update=update,
        context=context,
        state=state,
        text=text,
        photo_file_id=photo.file_id,
        reply_to_admin_message_id=reply_to,
    )
    await message.reply_text(
        "Спасибо за обращение. Техподдержка церковного сайта ответит вам в ближайшее время."
    )


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state: SupportState = context.application.bot_data["support_state"]
    message = update.message
    if not message.reply_to_message:
        return

    target_user_id = _extract_user_id_from_ticket(message.reply_to_message)
    if not target_user_id:
        await message.reply_text("Не удалось определить пользователя. Ответьте на сообщение обращения.")
        return

    if message.text:
        await context.bot.send_message(chat_id=target_user_id, text=message.text)
        return

    if message.photo:
        photo = message.photo[-1]
        await context.bot.send_photo(
            chat_id=target_user_id,
            photo=photo.file_id,
            caption=message.caption,
        )
        return

    if message.document:
        await context.bot.send_document(
            chat_id=target_user_id,
            document=message.document.file_id,
            caption=message.caption,
        )
        return

    await message.reply_text("Поддерживаются ответы текстом, фото и документом.")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    error_logger.error("Support bot handler failed", exc_info=context.error)


def build_application(bot_token: str, admin_chat_id: int) -> Application:
    app = Application.builder().token(bot_token).build()
    state = SupportState(admin_chat_id=admin_chat_id)
    state.load()
    app.bot_data["support_state"] = state

    user_filter = filters.ChatType.PRIVATE & (~filters.Chat(chat_id=admin_chat_id))
    admin_filter = filters.Chat(chat_id=admin_chat_id)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(user_filter & filters.TEXT & (~filters.COMMAND), handle_user_text)
    )
    app.add_handler(MessageHandler(user_filter & filters.PHOTO, handle_user_photo))
    app.add_handler(
        MessageHandler(
            admin_filter & (filters.TEXT | filters.PHOTO | filters.Document.ALL),
            handle_admin_reply,
        )
    )
    app.add_error_handler(on_error)
    return app


async def run() -> None:
    bot_token = os.getenv("BOT_TOKEN_HELP")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN_HELP is not set")

    admin_chat_raw = os.getenv("CHAT_ID")
    if not admin_chat_raw:
        raise RuntimeError("CHAT_ID is not set")

    admin_chat_id = int(admin_chat_raw)
    status_logger.info("Support bot started, admin_chat_id=%s", admin_chat_id)

    app = build_application(bot_token=bot_token, admin_chat_id=admin_chat_id)
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as ex:
        error_logger.error("Support bot failed", exc_info=ex)
        raise
