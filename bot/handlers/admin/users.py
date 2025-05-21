import logging
import persistent
import persistent.list
from pyrogram import Client
from pyrogram.types import Message
import utils

import globals as g

log = logging.getLogger("rhgTGBot:administration:users")



async def add_user(client: Client, message: Message):
    try:
        username = message.command[1]
    except:
        await message.reply_text("Имя пользователя не найдено.")
        return        
    
    user_info = await client.get_users(username)
    if not user_info:
        await message.reply_text(f"Пользователь {username} не найден")
        return
    
    with g.db.transaction() as conn:
        user = utils.db.create_user(user_info.id)
        conn.root.users[user_info.id] = user
    
    await message.reply_text(f"Пользователь {username} успешно добавлен")
    log.info(f"Пользователь {user_info.username} ({user_info.id}) успешно добавлен пользователем {message.from_user.username} ({message.from_user.id})")


async def del_user(client: Client, message: Message):
    try:
        username = message.command[1]
    except:
        await message.reply_text("Имя пользователя не найдено.")
        return        
    
    user_info = await client.get_users(username)
    if not user_info:
        await message.reply_text(f"Пользователь {username} не найден")
        return
    
    with g.db.transaction() as conn:
        del conn.root.users[user_info.id]
    
    await message.reply_text(f"Пользователь {username} успешно удален")
    log.info(f"Пользователь {user_info.username} ({user_info.id}) успешно удален пользователем {message.from_user.username} ({message.from_user.id})")


async def users_list(client: Client, message: Message):
    try:
        page = message.command[1] - 1
    except:
        page = 0
    
    users_list_strings = []
    with g.db.transaction() as conn:
        for index, tgid in enumerate(conn.root.users.keys()):
            if page * 10 <= index and index < (page * 10) + 10:
                users_list_strings.append(f"{index+1}. {conn.root.users[tgid]["username"]}")

    if not users_list_strings:
        await message.reply_text(f"Извините, но на странице {page+1} нет пользователей")
    else:
        await message.reply_text("Список пользователей:\n" + "\n".join(users_list_strings))
    
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) запросил информацию о пользователях.")