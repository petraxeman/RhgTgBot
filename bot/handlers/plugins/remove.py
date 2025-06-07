from pyrogram import Client
from pyrogram.types import Message

import globals as g



async def remove(client: Client, message: Message):
    if len(message.command) != 2:
        message.reply_text("Неправильные аргументы.")
        return
    
    codename = message.command[1]
    
    pd = await g.plugins.delete_one({"codename": codename})
    bd = await g.buckets.delete_many({"plugin": codename})
    cd = await g.code.delete_many({"plugin": codename})
    
    message.reply_text(f"**Удалено**\nПлагинов - {pd.deleted_count}\nБакетов - {bd.deleted_count}\nМодулей - {cd.deleted_count}")