from pyrogram import Client
from pyrogram.types import Message
import asyncio, utils, logging
import globals as g
from pyrogram.enums import ChatType, ChatAction

from pyrogram.handlers import MessageHandler
from pyrogram import filters

from . import settings
from . import talking
from . import profiles

log = logging.getLogger("rhgTGBot:gemini")


def include(bot, group: int):
    bot.add_handler(MessageHandler(settings.gmn_args, filters.command("gmn_args") & filters.private), group = group)
    bot.add_handler(MessageHandler(settings.set_gmn_arg, filters.command("set_gmn_arg") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.profiles, filters.command("profiles") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.clone_profile, filters.command("clone_profile") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.rename_profile, filters.command("rename_profile") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.select_profile, filters.command("select_profile") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.delete_profile, filters.command("delete_profile") & filters.private), group = group)


async def gemini_ask(client: Client, message: Message):
    if not message.text or message.text[0] in ["/", "!"]:
        return
    
    task = asyncio.create_task(utils.send_typing(message))
    message.sender = await g.users.find_one({"tgid": message.from_user.id})
    message.profile = await g.profiles.find_one({"owner": message.sender["tgid"], "name": message.sender["active_profile"]})
    
    try:
        if message.sender or message.profile:
            if message.profile.get("config", {}).get("token"):
                if message.chat.type == ChatType.PRIVATE:
                    result = await utils.access.process("ask", message.sender["rights"], message)
                    if result:
                        await talking.private_ask(client, message)
                    
                elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    result = await utils.access.process("private_ask", message.sender["rights"], message)
                    if result:
                        await talking.ask(client, message)
    finally:
        task.cancel()
        await client.send_chat_action(message.chat.id, ChatAction.CANCEL)