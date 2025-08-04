from pyrogram.handlers import MessageHandler
from pyrogram import filters

from pyrogram import Client, filters
from pyrogram.types import Message

import globals as g
import utils
import rexec



def include(bot, group: int):
    bot.add_handler(MessageHandler(stop_self_message, filters.outgoing), group = group)
    bot.add_handler(MessageHandler(prepare_private_command, filters.private & filters.regex(r"^\/(?P<command>[a-zA-Z]\S*)")), group = group)
    bot.add_handler(MessageHandler(pre_custom_command, filters.text & filters.private), group = group)


async def stop_self_message(client: Client, message: Message):
    message.stop_propagation()


async def prepare_private_command(client: Client, message: Message):
    user = await g.users.find_one({"tgid": message.from_user.id})
    if not user:
        return
    
    result = await utils.access.process(message.matches[0].group("command"), user["rights"] if user else [], message)
    if not result:
        message.stop_propagation()

    message.sender = user


async def pre_custom_command(client: Client, message: Message):
    if not message.text.startswith("!"):
        return
    
    user = await g.users.find_one({"tgid": message.from_user.id})
    if not user:
        return
    
    command = utils.parser.parse_command(message.text)
    plugin_codename = None
    for p in user["commands"]:
        if command[0] in user["commands"][p]:
            plugin_codename = p
            break
    if not plugin_codename:
        return
    
    method = None
    plugin = await g.plugins.find_one({"codename": plugin_codename})
    for c in plugin["commands"]:
        if c["command"] == command[0]:
            method = c["method"]
            break
    
    await rexec.gWorkerManager.execute_command(utils.parser.dump_message(message), plugin, method, command)
    
    message.stop_propagation()