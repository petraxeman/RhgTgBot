import logging
import os

import globals as g
from pyrogram import Client
from pyrogram.types import Message


log = logging.getLogger("rhgTGBot:utils:bot")


def setup_bot():
    bot = Client(
        "rhgTGBot",
        api_id = os.getenv("API_ID"),
        api_hash = os.getenv("API_HASH"),
        bot_token = os.getenv("BOT_TOKEN"),
        workdir = os.path.join(".", "assets", "sessions"))

    # g.API_ID = os.environ["API_ID"]
    # g.API_HASH = os.environ["API_HASH"]
    g.BOT_TOKEN = os.environ.get("BOT_TOKEN")

    del os.environ["API_ID"]
    del os.environ["API_HASH"]
    del os.environ["BOT_TOKEN"]

    log.info("Бот настроен.")

    return bot


async def initiate_bot(client):
    log.info("Получение информации о боте.")

    bot_info = await client.get_me()
    g.tg_bot_name = "@" + bot_info.username
    g.hr_bot_name = bot_info.first_name if not g.hr_bot_name else g.hr_bot_name

    log.info("Информации о боте получена.")


async def grab_messages(client: Client, message: Message, direction: dict):
    if direction["vector"] == 0:
        chat_id = message.chat.id
        curr_msg_id = message.id
        reply_usr_id = message.from_user.id
        vector = -1
    else:
        chat_id = message.reply_to_message.chat.id
        curr_msg_id = message.reply_to_message.id
        reply_usr_id = message.reply_to_message.from_user.id
        vector = direction["vector"]

    catched_messages = []
    strict = direction["strict"]
    count = direction["count"] if direction["count"] < 100 else 100

    catched_count = 0
    fallback = 0
    while catched_count < count:
        ids = [curr_msg_id + (i * vector) for i in range(20)]
        msgs = await client.get_messages(chat_id=chat_id, message_ids=ids)
        if strict:
            msgs = [msg for msg in msgs if hasattr(msg.from_user, "id") and msg.from_user.id == reply_usr_id]

        msgs = list(sorted(msgs, key=lambda x: x.id * -1))

        if fallback >= 3:
            break
        if not msgs:
            fallback += 1
            continue

        for msg in msgs:
            if (not msg.text) or (msg.chat.id != chat_id) or (catched_count >= count):
                continue

            catched_messages.append(f"- **{msg.from_user.username}** написал(а): {msg.text}\n")
            catched_count += 1

        curr_msg_id = msgs[-1].id + vector

    return "\n". join(["История чата сообщений:"] + catched_messages[::-1])


def message_has_archive(message: Message) -> bool:
    if message.document.file_name.endswith(".zip"):
        return True
    return False
