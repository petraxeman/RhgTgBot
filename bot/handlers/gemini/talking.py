import logging
from pyrogram import Client
from pyrogram.types import Message
import utils
from google.genai import types

import globals as g
import utils
import google.genai as genai

log = logging.getLogger("rhgTGBot:gemini:talking")

    

async def ask(client: Client, message: Message):
    flags, vector, clear_msg = utils.message.parse_ask_msg(message.text)
    
    params = utils.message.parse_flags(flags, message.profile['config'] or {})

    if params.get("forgot", False):
        message.profile = await g.profiles.update_one({"owner": message.from_user.id, "name": message.profile["name"]}, {"$set": {"chat": []}})
    
    if vector:
        message.profile['chat'].append({"role": "user", "parts": [{"text": await utils.bot.grab_messages(client, message, vector)}]})
    
    await process_ask(message, clear_msg, params)
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) совершил следующий запрос к Gemini: \"{clear_msg[:30]}\".")


async def private_ask(client: Client, message: Message):
    message.text = message.text.replace("@bot", g.tg_bot_name)
    flags, _, clear_msg = utils.message.parse_ask_msg(message.text)
    
    params = utils.message.parse_flags(flags, message.profile['config'] or {})

    if params.get("forgot", False):
        message.profile = await g.profiles.update_one({"owner": message.from_user.id, "name": message.profile["name"]}, {"$set": {"chat": []}})

    await process_ask(message, clear_msg, params)
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) совершил следующий частный запрос к Gemini: \"{clear_msg[:30]}\".")


async def process_ask(message: Message, request: str, params: dict):
    chat = message.profile["chat"]
    
    tools = []
    if params.get("search"):
        tools.append(types.Tool(google_search=types.GoogleSearchRetrieval()))
    
    chat.append({"role": "user", "parts": [{"text": request}]})
    credentials = f"Ты - {g.tg_bot_name} ({g.hr_bot_name}), а пользователь - {message.from_user.username}\n"
    
    response = await plain_ask(params, tools, chat, credentials)
    
    chat.append({"role": "model", "parts": [{"text": response}]})
    
    for text in utils.split_text(response):
        await message.reply_text(text)
    
    if not params.get("skipmsg"):
        while len(chat) > params.get("max_chat_size"):
            chat.pop(0)
        
        await g.profiles.update_one({"owner": message.from_user.id, "name": message.profile["name"]}, {"$set": {"chat": chat}})
            
    if params.get("delete"):
        await message.delete()


async def plain_ask(params, tools, chat, credentials):
    client = genai.Client(api_key=params.get("token"))
    response = await client.aio.models.generate_content(
        model = params.get("model"),
        config=types.GenerateContentConfig(
            system_instruction = [credentials + params.get("system_instruction")],
            tools = tools
            ),
        contents=chat,
    )
    return response.text