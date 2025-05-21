import logging, copy, re
from pyrogram import Client
from pyrogram.types import Message
import utils
import globals as g

log = logging.getLogger("rhgTGBot:gemini:profiles")



async def profiles(client: Client, message: Message):
    userid = message.from_user.id
    
    text = "Список ваших профилей:\n"
    with g.db.transaction() as conn:
        text += f"Текущий профиль - {conn.root.users[userid]["active_profile"]}\n"
        for i, profile_name in enumerate(conn.root.users[userid]["profiles"].keys()):
            text += f"{i+1}. {profile_name}\n"
    
    await message.reply_text(text)
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) запросил список профилей.")


async def clone_profile(client: Client, message: Message):
    userid = message.from_user.id
    profile_name = None
    if len(message.command) == 2:
        profile_name = message.command[1]
    
    with g.db.transaction() as conn:
        user = conn.root.users[userid]
        original_profile_name = user["active_profile"]
        if not profile_name:
            profile_name = original_profile_name + "_copy"
        
        if profile_name == "default" or profile_name in user["profiles"].keys():
            await message.reply_text(f"Вы не можете создать новый профиль с именем '{profile_name}'.")
            return
    
        profile = user["profiles"].get(original_profile_name)
        user["profiles"][profile_name] = copy.deepcopy(profile)
        conn.root.users[userid] = user
        
    await message.reply_text(f"Была создана копия текущего профиля под названием {profile_name}")
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) сделал копию профиля {original_profile_name} под названием {profile_name}.")


async def select_profile(client: Client, message: Message):
    userid = message.from_user.id
    if len(message.command) != 2:
        await message.reply_text("Неправильные аргументы.")
        return
    
    profile_name = message.command[1]
    
    with g.db.transaction() as conn:
        user = conn.root.users[userid]
        
        if not profile_name in user["profiles"].keys():
            await message.reply_text(f"Профиль {profile_name} не найден.")
            return
        
        user["active_profile"] = profile_name
        conn.root.users[userid] = user
        
    await message.reply_text(f"Вы выбрали профиль {profile_name}")
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) переключился на профил {profile_name}.")


async def rename_profile(client: Client, message: Message):
    userid = message.from_user.id
    original_profile_name = None
    if len(message.command) == 3:
        original_profile_name, profile_name = message.command[1], message.command[2]
    elif len(message.command) == 2:
        profile_name = message.command[1]
    else:
        await message.reply_text("Неправильные аргументы.")
        return
    
    with g.db.transaction() as conn:
        user = conn.root.users[userid]
        profile_names = user["profiles"].keys()
        original_profile_name = user["active_profile"] if not original_profile_name else original_profile_name
        
        if profile_name == "default" or original_profile_name == "default" or profile_name in profile_names:
            await message.reply_text(f"Вы не можете переименовать текущий профиль на '{profile_name}'.")
            return
        
        user["profiles"][profile_name] = user["profiles"].get(original_profile_name)
        del user["profiles"][original_profile_name]

        if original_profile_name == user["active_profile"]:
            user["active_profile"] = profile_name
        
        conn.root.users[userid] = user
    
    await message.reply_text(f"Вы успешно переименовали профиль {original_profile_name} в {profile_name}")
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) переименовал профиль {original_profile_name} в {profile_name}.")


async def delete_profile(client: Client, message: Message):
    userid = message.from_user.id
    if len(message.command) == 2:
        profile_name = message.command[1]
    else:
        await message.reply_text("Неправильные аргументы.")
        return
    
    if profile_name == "default":
        await message.reply_text("Вы не можете удалить профиль 'default'.")
        return
    
    with g.db.transaction() as conn:
        user = conn.root.users[userid]
        if not profile_name in user["profiles"].keys():
            await message.reply_text(f"Профиль {profile_name} не найден.")
            return
        
        if profile_name == user["active_profile"]:
            user["active_profile"] = "default"
        
        del user["profiles"][profile_name]
        user = conn.root.users[userid]
    
    await message.reply_text(f"Вы удалили профиль {profile_name}")
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) удалил профиль {profile_name}.")
        