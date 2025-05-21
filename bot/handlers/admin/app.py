import logging
from pyrogram import Client
from pyrogram.types import Message
import utils

import globals as g

log = logging.getLogger("rhgTGBot:administration:app")

APP_SETTINGS = {
    "default_rights": "string",
    "hr_bot_name": "string"
}



async def app_args(client: Client, message: Message):
    text = "Сейчас установлены следующие настройки:\n"
    with g.db.transaction() as conn:
        config = conn.root.config
        
        for setting in APP_SETTINGS.keys():
            text += f"{setting}: {config.get(setting)}\n"
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) запросил информацию о настройках приложения.")
    
    await message.reply_text(text)


async def set_app_arg(client: Client, message: Message):
    if len(message.command) != 3:
        await message.reply_text("Неправильные аргументы.")

    arg, val = message.command[1], message.command[2]
    if ( val not in APP_SETTINGS.get(arg, tuple()) ) and ( APP_SETTINGS.get(arg) != "string"):
        log.warning(f"Пользователь {message.from_user.username} ({message.from_user.id}) установил пыталсяя установить настройку прилажения {arg} на {val}. Это неверный аргумент.")
        await message.reply_text("Неправильные аргументы.")
    
    with g.db.transaction() as conn:
        conn.root.config[arg] = val
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) установил настройку прилажения {arg} на {val}")
    
    await message.reply_text(f"Вы установили настройку {arg} на {val}")
    
    
    

