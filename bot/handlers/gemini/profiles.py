import logging
from pyrogram import Client
from pyrogram.types import Message
import globals as g

log = logging.getLogger("rhgTGBot:gemini:profiles")



async def profiles(client: Client, message: Message):
    text = "Список ваших профилей:\n"
    text += f"Текущий профиль - {message.sender['active_profile']}\n"
    for i, profile_name in enumerate(message.sender['profiles']):
        text += f"{i+1}. {profile_name}\n"
    
    await message.reply_text(text)
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) запросил список профилей.")


async def clone_profile(client: Client, message: Message):
    profile_name = None
    if len(message.command) == 2:
        profile_name = message.command[1]
    
    original_profile = await g.profiles.find_one({"owner": message.from_user.id, "name": message.sender['active_profile']}, {"_id": 0})
    if not profile_name:
        original_profile['name'] += "_copy"
    else:
        original_profile['name'] = profile_name
    
    await g.profiles.insert_one(original_profile)
    await g.users.update_one({"tgid": message.from_user.id}, {"$push": {"profiles": original_profile['name']}})

    await message.reply_text(f"Была создана копия текущего профиля под названием {profile_name}")
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) сделал копию профиля {original_profile['name']} под названием {profile_name}.")


async def select_profile(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Неправильные аргументы.")
        return
    
    profile_name = message.command[1]
    
    if profile_name in message.sender['profiles']:
        await g.users.update_one({"tgid": message.from_user.id}, {"$set": {"active_profile": profile_name}})
        
    await message.reply_text(f"Вы выбрали профиль {profile_name}")
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) переключился на профил {profile_name}.")


async def rename_profile(client: Client, message: Message):
    original_profile_name = None
    if len(message.command) == 3:
        original_profile_name, profile_name = message.command[1], message.command[2]
    elif len(message.command) == 2:
        profile_name = message.command[1]
    else:
        await message.reply_text("Неправильные аргументы.")
        return
    
    if profile_name == "default" or original_profile_name == "default":
        await message.reply_text("Вы не можете переименовать профиль 'default', или назвать какой либо профиль 'default'.")
        return
    
    await g.users.update_one({"tgid": message.from_user.id}, {"$pull": {"profiles": original_profile_name}})
    await g.profiles.update_one({"owner": message.from_user.id, "name": original_profile_name}, {"$set": {"name": profile_name}})
    await g.users.update_one({"tgid": message.from_user.id}, {"$push": {"profiles": profile_name}})
    
    await message.reply_text(f"Вы успешно переименовали профиль {original_profile_name} в {profile_name}")
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) переименовал профиль {original_profile_name} в {profile_name}.")


async def delete_profile(client: Client, message: Message):
    if len(message.command) == 2:
        profile_name = message.command[1]
    else:
        await message.reply_text("Неправильные аргументы.")
        return
    
    if profile_name == "default":
        await message.reply_text("Вы не можете удалить профиль 'default'.")
        return
    
    if not profile_name in message.sender["profiles"]:
        await message.reply_text(f"Профиль {profile_name} не найден.")
        return
    
    if profile_name == message.sender["active_profile"]:
        await g.users.update_one({"tgid": message.from_user.id}, {"$set": {"active_profile": "default"}})
    await g.profiles.delete_one({"owner": message.from_user.id, "name": profile_name})
    await g.users.update_one({"tgid": message.from_user.id}, {"$pull": {"profiles": profile_name}})
    
    await message.reply_text(f"Вы удалили профиль {profile_name}")
    log.info(f"Пользователь {message.from_user.username} ({message.from_user.id}) удалил профиль {profile_name}.")
        