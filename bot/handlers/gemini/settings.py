import logging, re 
from pyrogram import Client
from pyrogram.types import Message
import utils

import globals as g

log = logging.getLogger("rhgTGBot:gemini:settings")

GEMINI_ARGS = {
    "token": {"type": "string", "hide": True},
    "forgot": {"type": "bool"},
    "search": {"type": "bool"},
    "delete": {"type": "bool"},
    "skipmsg": {"type": "bool"},
    "model": {"type": "string", "variants": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.5-flash-preview-04-17"]},
    "max_chat_size": {"type": "int"},
    "system_instruction": {"type": "string", "long": True}   
}



async def gmn_args(client: Client, message: Message):
    userid = message.from_user.id
    profile_name = None
    if len(message.command) == 2:
        profile_name = message.command[1]
    
    text = ""
    with g.db.transaction() as conn:
        user = conn.root.users[userid]
        profile_name = user["active_profile"] if not profile_name else profile_name
        profile = user["profiles"].get(profile_name)
        if not profile:
            await message.reply_text(f"Профиль '{profile_name}' не найден.")
            return
        
        text += f"Настройки профиля {profile_name}:\n"
        for arg in GEMINI_ARGS.keys():
            value = str(profile["config"].get(arg))
            if GEMINI_ARGS.get(arg, {}).get("hide"):
                part = len(value) / 10
                value = ("•" * int(part * 5)) + value[int(part * 9):]
            
            text += f"{arg}: {value}\n"
        
        conn.root.users[userid] = user
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) запросил информацию о настройках профиля {profile_name}.")
    
    await message.reply_text(text)


async def set_gmn_arg(client: Client, message: Message):
    try:
        m = re.search(r"^\/set_gmn_arg (?P<arg>[a-z_]+) (?P<val>[\s\S]*)", message.text)
        arg = m.group("arg")
        val = m.group("val").strip()
    except:
        await message.reply_text("Неправильные аргументы.")
        return
    
    userid = message.from_user.id
    arg_ref = GEMINI_ARGS.get(arg)
    
    if arg_ref.get("variants") and val not in arg_ref.get("variants"):
        await message.reply_text(f"Неправильное значение. В поле {arg} разрешены только следующие значения: {', '.join(arg_ref.get('variants'))}")
        return
    
    setted_value = None
    with g.db.transaction() as conn:
        user = conn.root.users[userid]
        
        profile_name = user["active_profile"]
        profile = user["profiles"].get(profile_name)
        
        match arg_ref.get("type"):
            case "string":
                setted_value = val
                profile["config"][arg] = val
            case "bool":
                setted_value = utils.cast_to_bool(val)
                profile["config"][arg] = setted_value
            case "int":
                setted_value = utils.cast_to_int(val)
                if setted_value:
                    profile["config"][arg] = setted_value
        
        conn.root.users[userid] = user
    
    if setted_value is not None:
        await message.reply_text(f"Вы установили параметр {arg} на {setted_value}")
        log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) установил параметр {arg} в профиле {profile_name}.")
    else:
        await message.reply_text(f"Вы не установили параметр. {val} неправильное значение.")
        log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) пытался установить неправильный параметр {arg}.")