import logging
from pyrogram import Client
from pyrogram.types import Message

import globals as g

log = logging.getLogger("rhgTGBot:administration:rights")



async def add_right(client: Client, message: Message):
    try:
        username = message.command[1]
        right = message.command[2]
    except:
        await message.reply_text("Переданы неправельные аргументы.")
    
    user_info = await client.get_users(username)
    await g.db.users.update_one({"tgid": user_info.id}, {"$push": {"rights": right}})
    
    await message.reply_text(f"Для пользователяя {username} установлено право {right}")
    if message.from_user.id != user_info.id:
        await client.send_message(user_info.id, f"Для вас установлено право {right}")

    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) установил право {right} пользователю {username}")


async def del_right(client: Client, message: Message):
    try:
        username = message.command[1]
        right = message.command[2]
    except:
        await message.reply_text("Переданы неправельные аргументы.")
    
    user_info = await client.get_users(username)
    await g.db.users.update_one({"tgid": user_info.id}, {"$pull": {"rights": right}})
    
    await message.reply_text(f"У пользователя {username} удалено право {right}")
    if message.from_user.id != user_info.id:
        await client.send_message(user_info.id, f"У вас удалено право {right}")
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) удалил право {right} у пользователя {username}")


async def show_rights(client: Client, message: Message):
    try:
        if {"adm:show_rights", "adm:gr:rights", "adm:full", "all:full"}.intersection(message.sender["rights"]):
            username = message.command[1]
        else:
            username = None
    except:
        username = None
    
    if not username and {"adm:show_self_rights", "adm:show_rights", "adm:gr:rights", "adm:full", "all:full"}.intersection(message.sender["rights"]):
        username = message.from_user.username
    elif not username:
        log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) пытался запросить информацию о правах {username} без прав на это.")
        return
    
    user_info = await client.get_users(username)
    
    response = ""
    for i, right in enumerate((await g.users.find_one({"tgid": user_info.id}))["rights"]):
        response += f"{i+1}. {right}\n"
    
    if not response: response = "У пользователя нет прав."
    
    await message.reply_text(f"Пользователь {username} имеет следующие права:\n{response}")
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) запросил информацию о правах пользователя {username}")