import os, logging, re
from pyrogram import Client
from pyrogram.types import Message
import globals as g
from . import db, xor

log = logging.getLogger("rhgTGBot:setup")



def setup_bot():
    bot = Client(
        "rhgTGBot",
        api_id = os.getenv("API_ID"),
        api_hash = os.getenv("API_HASH"),
        bot_token = os.getenv("BOT_TOKEN"),
        workdir = os.path.join(".", "assets", "sessions"))
    
    del os.environ["API_ID"]
    del os.environ["API_HASH"]
    del os.environ["BOT_TOKEN"]
    
    log.info("Бот настроен.")
    
    return bot


async def initiate_admin(client):
    user_info = await client.get_users(g.owner_username)
    log.info("Настройка админа.")
    with g.db.transaction() as conn:
        if not user_info.id in conn.root.users or g.cfg.get("SETUP", {}).get("reload_config", False):
            user = db.User(user_info.username, user_info.id)
            user.rights.append("all:full")
            conn.root.users[user_info.id] = user
    log.info("Админ настроен.")


async def initiate_bot(client):
    log.info("Получение информации о боте.")

    bot_info = await client.get_me()
    g.tg_bot_name = "@" + bot_info.username
    g.hr_bot_name = bot_info.first_name if not g.hr_bot_name else g.hr_bot_name
    
    log.info("Информации о боте получена.")


def parse_ask_msg(text: str):
    regex = f"(?P<full_command>{g.tg_bot_name}[!/#]?(?P<flags>[fsdn012]+)?(?P<vector>=?[+-~]\\d*)?)"
    match = re.match(regex, text)
    
    flags = ""
    vector = ""
    clear_msg = text
    if match:
        flags = match.group("flags")
        vector = match.group("vector")
        clear_msg = text.replace(match.group("full_command"), g.hr_bot_name)
    
    flags = set(flags) if flags else set()
    vector = parse_vector(vector) if vector else {}
    return flags, vector, clear_msg


def parse_vector(direction: str):
    match = re.match(r"(?P<exact>=)?(?P<vector>[+-~])(?P<count>\d+)?", direction)
    data = {}
    data["strict"] = True if match.group("exact") else False

    match match.group("vector"):
        case "+":
            data["vector"] = -1
        case "-":
            data["vector"] = 1
        case "~":
            data["vector"] = 0
    
    try:
        data["count"] = int(match.group("count"))
        if data["count"] > 300:
            data["count"] = 300
        elif data["count"] < 1:
            data["count"] = 1
    except:
        data["count"] = 10
    
    return data


def parse_flags(flags: str, params: dict):
    new_params = {"token": params.get("token")}
    flags = set(flags)
    
    new_params["forgot"] = True if xor("f" in flags, params.get("forgot", False)) else False
    new_params["search"] = True if xor("s" in flags, params.get("search", False)) else False
    new_params["delete"] = True if xor("d" in flags, params.get("delete", False)) else False
    new_params["skip_msg"] = True if xor("n" in flags, params.get("skipmsg", False)) else False
    new_params["system_instruction"] = params.get("system_instruction", "")
    new_params["max_chat_size"] = params.get("max_chat_size", 15)
    
    if "0" in flags: new_params["model"] = "gemini-1.5-flash"
    elif "1" in flags: new_params["model"] = "gemini-2.0-flash"
    elif "2" in flags: new_params["model"] = "gemini-2.5-flash-preview-04-17"
    elif params.get("model"): new_params["model"] = params.get("model")
    else: new_params["model"] = "gemini-2.0-flash"
    
    return new_params


async def grab_messages(client: Client, message: Message, direction: dict):
    if direction["vector"] == 0:
        chat_id = message.chat.id
        curr_msg_id = message.id
        reply_usr_id = message.from_user.id
        vector = -1
    else:
        chat_id = message.reply_to_message.chat.id
        curr_msg_id = message.reply_to_message.id
        reply_usr_id = message.reply_to_message.from_user.id
        vector = direction["vector"]
    
    catched_messages = []
    strict = direction["strict"]
    count = direction["count"] if direction["count"] < 100 else 100
    
    catched_count = 0; fallback = 0
    while catched_count < count:
        ids = [curr_msg_id + (i * vector) for i in range(20)]
        msgs = await client.get_messages(chat_id=chat_id, message_ids=ids)
        if strict:
            msgs = [msg for msg in msgs if hasattr(msg.from_user, "id") and msg.from_user.id == reply_usr_id]
        
        msgs = list(sorted(msgs, key=lambda x: x.id * -1))
        
        if fallback >= 3:
            break
        if not msgs:
            fallback += 1
            continue
            
        for msg in msgs:
            if (not msg.text) or (msg.chat.id != chat_id) or (catched_count >= count):
                continue
            
            catched_messages.append(f"- **{msg.from_user.username}** написал(а): {msg.text}\n")
            catched_count += 1
        
        curr_msg_id = msgs[-1].id + vector
    
    return "\n". join(["История чата сообщений:"] + catched_messages[::-1])