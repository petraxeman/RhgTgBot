import logging
from pyrogram import Client
from pyrogram.types import Message
import utils

import globals as g
import utils.message

log = logging.getLogger("rhgTGBot:gemini:talking")

    

async def ask(client: Client, message: Message):
    user_id = message.from_user.id
    
    flags, vector, clear_msg = utils.message.parse_ask_msg(message.text)
    
    with g.db.transaction() as conn:
        profile_names = conn.root.users[user_id].active_profile
        profile = conn.root.users[user_id].profiles.get(profile_names)
        chat = list(profile.chat)
        user_params = dict(profile.config)
    
    params = utils.message.parse_flags(flags, user_params or {})

    if params.get("forgot", False):
        with g.db.transaction() as conn:
            profile_name = conn.root.users[user_id].active_profile
            profile = conn.root.users[user_id].profiles.get(profile_name)
            profile.chat = []
    
    if vector:
        chat.append({"role": "user", "parts": [{"text": await utils.bot.grab_messages(client, message, vector)}]})
    
    await utils.ai.ask(message, clear_msg, chat, params)
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) совершил следующий запрос к Gemini: \"{clear_msg[:30]}\".")


async def private_ask(client: Client, message: Message):
    user_id = message.from_user.id
    message.text = message.text.replace("@bot", g.tg_bot_name)
    flags, _, clear_msg = utils.message.parse_ask_msg(message.text)
    
    with g.db.transaction() as conn:
        profile_names = conn.root.users[user_id].active_profile
        profile = conn.root.users[user_id].profiles.get(profile_names)
        chat = list(profile.chat)
        user_params = dict(profile.config)
    
    params = utils.bot.parse_flags(flags, user_params or {})

    if params.get("forgot", False):
        with g.db.transaction() as conn:
            profile_name = conn.root.users[user_id].active_profile
            profile = conn.root.users[user_id].profiles.get(profile_name)
            profile.chat = []

    await utils.ai.ask(message, clear_msg, chat, params)
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) совершил следующий частный запрос к Gemini: \"{clear_msg[:30]}\".")