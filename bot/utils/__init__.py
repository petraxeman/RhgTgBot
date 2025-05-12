import asyncio
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction

true = ["t", "true", "yes", "y", "1", "д", "да"]
false = ["f", "false", "no", "n", "0", "н", "нет"]



def cast_to_bool(var: str) -> bool:
    if var.lower() in true:
        return True
    elif var.lower() in false:
        return False
    return False


def cast_to_int(var: str) -> int:
    try:
        return int(var)
    except:
        return None


def xor(f: bool, s: bool):
    return (f or s) and not (f and s)


def split_text(original_text: str, max_size = 4096):
    texts = []
    current_text = ""
    
    for word in original_text.split(" "):
        if len(current_text + " " + word) < max_size:
            current_text += " " + word
        else:
            texts.append(current_text)
            current_text = ""

    if current_text:
        texts.append(current_text)
    
    return texts


async def send_typing(message: Message):
    while True:
        await message.reply_chat_action(ChatAction.TYPING)
        await asyncio.sleep(5)


from . import bot, db, access, ai, message