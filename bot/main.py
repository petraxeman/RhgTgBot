import logging, os, sys, traceback
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(".", "logs", datetime.strftime(datetime.now(), "%d.%m.%Y %H-%M %S.log"))),
        logging.FileHandler(os.path.join(".", "logs", "latest.log"), mode="w"),
        logging.StreamHandler()
    ]
)
sys.excepthook = lambda t, v, tb: logging.critical(f"Uncaught exception: {str(v)}\n{''.join(traceback.format_tb(tb))}")

log = logging.getLogger("rhgTGBot:main")

import asyncio, pyrogram, enum, uvloop, traceback
import globals as g

from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatAction

import utils, handlers



PRELUDE = -1
ADM = 0
INFO = 1
ACCOUNT = 2
PROJECT = 3
GEMINI = 15




async def pre_private_command(client: Client, message: Message):
    with g.db.transaction() as conn:
        try:
            user = conn.root.users[message.from_user.id]
        except KeyError:
            user = None
        
        result = await utils.access.process(message.matches[0].group("command"), user["rights"] if user else [], message, log)

        message.sender_rights = list(user["rights"])
    
    if not result:
        message.stop_propagation()


async def gemini_ask(client: Client, message: Message):
    if not message.text or message.text[0] in ["/", "!"]:
        return
    userid = message.from_user.id
    task = asyncio.create_task(utils.send_typing(message))
    try:
        with g.db.transaction() as conn:
            user_rights = list(conn.root.users[userid]["rights"])
            profile_name = conn.root.users[userid]["active_profile"]
            token = conn.root.users[userid]["profiles"].get(profile_name, {}).get("config", {}).get("token", "")
        
        if not token or len(token) < 20:
            return
        
        if message.chat.type == ChatType.PRIVATE:
            result = await utils.access.process("ask", user_rights, message, log)
            if not result:
                return
            await handlers.gemini.talking.private_ask(client, message)
            
        elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            result = await utils.access.process("private_ask", user_rights, message, log)
            if not result:
                return
            await handlers.gemini.talking.ask(client, message)
    finally:
        task.cancel()
        await bot.send_chat_action(message.chat.id, ChatAction.CANCEL)
   

async def transfer(client: Client, message: Message):
    if message.from_user.username == g.owner_username:
        try:
            new_owner_username = message.command[1]
        except:
            return

        with g.db.transaction() as conn:
            conn.root.config["owner_username"] = new_owner_username
        
        g.init_const()
        
        try:
            await client.send_message(new_owner_username, "Теперь вы мой владелец.")
            await message.reply_text("Вы больше не владелец.")
        except:
            await message.reply_text("Кажется мой владелец еще не существует.")
        
        log.info(f"Трансфер успешно проведен. Бывший админ {message.from_user.username}. Новый админ {new_owner_username}")


async def main():
    await bot.start()
    
    log.info("Бот запущен.")
    
    bot.add_handler(MessageHandler(transfer, filters.command("transfer") & filters.private), group = PRELUDE)
    bot.add_handler(MessageHandler(pre_private_command, filters.private & filters.regex(r"^\/(?P<command>[a-zA-Z]\S*)")), group = PRELUDE)
    handlers.admin.include(bot, ADM)
    handlers.info.include(bot, INFO)
    handlers.project.include(bot, PROJECT)
    handlers.gemini.include(bot, GEMINI)
    bot.add_handler(MessageHandler(gemini_ask, filters.mentioned | filters.private), group = GEMINI)
    
    log.info("Обработчики созданы.")
    
    await utils.db.initiate_admin(bot)
    await utils.bot.initiate_bot(bot)
    
    try:
        log.info("Запускаем бесконечный цикл.")
        await pyrogram.idle()
    except KeyboardInterrupt:
        log.info("Получен сигнал KeyboardInterrupt. Завершение...")
        await bot.stop()
        quit()


if __name__ == "__main__":
    log.info("Инициализация базы данных")
    
    utils.db.initiate_derictories()
    utils.db.initiate_database(g.db)
    g.init_const()
    
    bot = utils.bot.setup_bot()
    
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    #uvloop.install()
    bot.run(main())