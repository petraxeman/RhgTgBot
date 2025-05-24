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
    user = await g.users.find_one({"tgid": message.from_user.id})
    
    result = await utils.access.process(message.matches[0].group("command"), user["rights"] if user else [], message, log)
    
    if not result:
        message.stop_propagation()
    
    message.sender = user


async def gemini_ask(client: Client, message: Message):
    if not message.text or message.text[0] in ["/", "!"]:
        return
    
    task = asyncio.create_task(utils.send_typing(message))
    message.sender = await g.users.find_one({"tgid": message.from_user.id})
    message.profile = await g.profiles.find_one({"owner": message.sender["tgid"], "name": message.sender["active_profile"]})
    
    try:
        if message.sender or message.profile:
            if message.profile.get("config", {}).get("token"):
                if message.chat.type == ChatType.PRIVATE:
                    result = await utils.access.process("ask", message.sender["rights"], message, log)
                    if result:
                        await handlers.gemini.talking.private_ask(client, message)
                    
                elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    result = await utils.access.process("private_ask", message.sender["rights"], message, log)
                    if result:
                        await handlers.gemini.talking.ask(client, message)
    finally:
        task.cancel()
        await bot.send_chat_action(message.chat.id, ChatAction.CANCEL)


async def main():
    await bot.start()
    
    log.info("Бот запущен.")
    
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
    
    bot = utils.bot.setup_bot()
    
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    #uvloop.install()
    bot.run(main())