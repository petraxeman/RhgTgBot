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
    profile = await g.profiles.find_one({"owner": message.sender["tgid"], "name": message.sender["active_profile"]})
    
    text = f"Настройки профиля {profile['name']}:\n"
    for arg in GEMINI_ARGS.keys():
        value = str(profile["config"].get(arg))
        if GEMINI_ARGS.get(arg, {}).get("hide"):
            part = len(value) / 10
            value = ("•" * int(part * 5)) + value[int(part * 9):]
        
        text += f"{arg}: {value}\n"
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) запросил информацию о настройках профиля {profile['name']}.")
    
    await message.reply_text(text)


async def set_gmn_arg(client: Client, message: Message):
    try:
        m = re.search(r"^\/set_gmn_arg (?P<arg>[a-z_]+) (?P<val>[\s\S]*)", message.text)
        arg = m.group("arg")
        val = m.group("val").strip()
    except:
        await message.reply_text("Неправильные аргументы.")
        return
    
    arg_ref = GEMINI_ARGS.get(arg)
    
    if arg_ref.get("variants") and val not in arg_ref.get("variants"):
        await message.reply_text(f"Неправильное значение. В поле {arg} разрешены только следующие значения: {', '.join(arg_ref.get('variants'))}")
        return
    
    setted_value = None
    
    profile = await g.profiles.find_one({"owner": message.sender["tgid"], "name": message.sender["active_profile"]})
    match arg_ref.get("type"):
        case "string":
            setted_value = val
            await g.profiles.update_one({"owner": message.sender["tgid"], "name": profile["name"]}, {"$set": {"config." + arg: setted_value}})
        case "bool":
            setted_value = utils.cast_to_bool(val)
            await g.profiles.update_one({"owner": message.sender["tgid"], "name": profile["name"]}, {"$set": {"config." + arg: setted_value}})
        case "int":
            setted_value = utils.cast_to_int(val)
            if setted_value:
                await g.profiles.update_one({"owner": message.sender["tgid"], "name": profile["name"]}, {"$set": {"config." + arg: setted_value}})
    
    if setted_value is not None:
        await message.reply_text(f"Вы установили параметр {arg} на {setted_value}")
        log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) установил параметр {arg} в профиле {profile['name']}.")
    else:
        await message.reply_text(f"Вы не установили параметр. {val} неправильное значение.")
        log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) пытался установить неправильный параметр {arg}.")