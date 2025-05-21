from pyrogram.handlers import MessageHandler
from pyrogram import filters

from . import settings
from . import talking
from . import profiles



def include(bot, group: int):
    bot.add_handler(MessageHandler(settings.gmn_args, filters.command("gmn_args") & filters.private), group = group)
    bot.add_handler(MessageHandler(settings.set_gmn_arg, filters.command("set_gmn_arg") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.profiles, filters.command("profiles") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.clone_profile, filters.command("clone_profile") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.rename_profile, filters.command("rename_profile") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.select_profile, filters.command("select_profile") & filters.private), group = group)
    bot.add_handler(MessageHandler(profiles.delete_profile, filters.command("delete_profile") & filters.private), group = group)