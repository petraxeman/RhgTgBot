from pyrogram import filters
from pyrogram.handlers import MessageHandler

from . import (
    app,
    rights,
    users
)


def include(bot, group: int):
    bot.add_handler(MessageHandler(users.add_user, filters.command("add_user") & filters.private), group = group)
    bot.add_handler(MessageHandler(users.del_user, filters.command("del_user") & filters.private), group = group)
    bot.add_handler(MessageHandler(users.users_list, filters.command("users_list") & filters.private), group = group)
    bot.add_handler(MessageHandler(rights.add_right, filters.command("add_right") & filters.private), group = group)
    bot.add_handler(MessageHandler(rights.del_right, filters.command("sub_right") & filters.private), group = group)
    bot.add_handler(MessageHandler(rights.show_rights, filters.command("show_rights") & filters.private), group = group)
    bot.add_handler(MessageHandler(app.app_args, filters.command("app_args") & filters.private), group = group)
    bot.add_handler(MessageHandler(app.set_app_arg, filters.command("set_app_arg") & filters.private), group = group)
