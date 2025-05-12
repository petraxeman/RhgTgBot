from pyrogram.types import Message
from google.genai import types
from . import split_text
import google.genai as genai
import globals as g



async def ask(message: Message, request: str, chat: list, params: dict):
    user_id = message.from_user.id

    tools = []
    if params.get("search"):
        tools.append(types.Tool(google_search=types.GoogleSearchRetrieval()))
    
    chat.append({"role": "user", "parts": [{"text": request}]})
    credentials = f"Ты - {g.tg_bot_name} ({g.hr_bot_name}), а пользователь - {message.from_user.username}\n"
    
    client = genai.Client(api_key=params.get("token"))

    response = await plain_ask(client, params, tools, chat, credentials)
    
    chat.append({"role": "model", "parts": [{"text": response}]})
    
    for text in split_text(response):
        await message.reply_text(text)
    
    if not params.get("skipmsg"):
        while len(chat) > params.get("max_chat_size"):
            chat.pop(0)
        
        with g.db.transaction() as conn:
            profile_name = conn.root.users[user_id].active_profile
            conn.root.users[user_id].profiles[profile_name].chat = chat
    
    if params.get("delete"):
        await message.delete()


async def plain_ask(client, params, tools, chat, credentials):
    response = await client.aio.models.generate_content(
        model = params.get("model"),
        config=types.GenerateContentConfig(
            system_instruction = [credentials + params.get("system_instruction")],
            tools = tools
            ),
        contents=chat,
    )
    return response.text