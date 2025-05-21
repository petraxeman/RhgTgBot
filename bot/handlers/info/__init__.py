from pyrogram.handlers import MessageHandler
from pyrogram import filters

from . import help
from . import start



def include(bot, group: int):
    bot.add_handler(MessageHandler(start.start_command, filters.command("start") & filters.private), group = group)
    bot.add_handler(MessageHandler(help.help_command, filters.command("help") & filters.private), group = group)