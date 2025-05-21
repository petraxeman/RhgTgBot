from pyrogram.handlers import MessageHandler
from pyrogram import filters

from . import upload



def include(bot, group):
    bot.add_handler(MessageHandler(upload.upload_project, filters.command("upload_project") & filters.private), group = group)