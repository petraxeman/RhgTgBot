import logging
from pyrogram import Client
from pyrogram.types import Message

import globals as g

log = logging.getLogger("rhgTGBot:info:start")



async def start_command(client: Client, message: Message):
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) вызвал стартовое сообщение")
    await message.reply_text(
        f"Привет! Я rhgTGbot. Меня зовут {g.hr_bot_name}\n"
        "Что бы узнать о моих возможностях можешь вызвать /help"
    )