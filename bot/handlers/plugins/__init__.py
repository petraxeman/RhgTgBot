from pyrogram.handlers import MessageHandler
from pyrogram import filters

from . import upload, follow, update, remove



def include(bot, group):
    bot.add_handler(MessageHandler(upload.upload_plugin, filters.command("upload_plugin") & filters.private), group = group)
    bot.add_handler(MessageHandler(update.update, filters.command("update") & filters.private), group = group)
    bot.add_handler(MessageHandler(remove.remove, filters.command("update") & filters.private), group = group)
    bot.add_handler(MessageHandler(follow.follow, filters.command("follow") & filters.private), group = group)
