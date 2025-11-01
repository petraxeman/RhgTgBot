import logging

import globals as g
import utils
from pyrogram import Client
from pyrogram.types import Message


log = logging.getLogger("rhgTGBot:administration:app")

APP_SETTINGS = {
    "default_rights": "string",
    "hr_bot_name": "string"
}


async def app_args(client: Client, message: Message):
    text = "Сейчас установлены следующие настройки:\n"

    variables = await g.client.rhgtgbotdb.meta.find_one({"type": "global_variables"})

    for setting in APP_SETTINGS.keys():
        text += f"{setting}: {variables.get(setting)}\n"

    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) запросил информацию о настройках приложения.")

    await message.reply_text(text)


async def set_app_arg(client: Client, message: Message):
    if len(message.command) != 3:
        await message.reply_text("Неправильные аргументы.")
    arg, val = message.command[1], message.command[2]

    if arg not in APP_SETTINGS.keys():
        log.warning(f"Пользователь {message.from_user.username} ({message.from_user.id}) установил пыталсяя установить настройку прилажения {arg} на {val}. Это неверный аргумент.")
        await message.reply_text("Неправильные аргументы.")

    match arg:
        case "default_rights":
            await g.client.rhgtgbotdb.meta.update_one({"type": "global_variables"}, {"$set": {"default_rights": val.replace(" ", "").split(",")}})
        case "hr_bot_name":
            await g.client.rhgtgbotdb.meta.update_one({"type": "global_variables"}, {"$set": {"hr_bot_name": val}})

    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) установил настройку прилажения {arg} на {val}")

    await message.reply_text(f"Вы установили настройку {arg} на {val}")
