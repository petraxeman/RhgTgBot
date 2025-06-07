import logging
from pyrogram import Client
from pyrogram.types import Message
import globals as g
import utils, os, git, yaml, re

log = logging.getLogger("rhgTGBot:plugins:follow")



async def follow(client: Client, message: Message):
    try:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]+", message.command[1]): raise Exception("Wrong plugin name")
    except:
        await message.reply_text("Неправильное имя плагина.")
    
    plugin = await g.plugins.find_one({"codename": message.command[1]})
    commands = [c["command"] for c in plugin["commands"]]

    await g.users.update_one({"tgid": message.sender["tgid"]}, {"$set": {"commands": {plugin["codename"]: commands}}})
    await message.reply_text(f"Вы успешно подписались на плагин {plugin['name']}")