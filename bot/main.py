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

apsheduler_logger = logging.getLogger('apscheduler')
apsheduler_logger.propagate = False
del apsheduler_logger

import asyncio, pyrogram, traceback
import globals as g

from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from pyrogram.types import Message

import utils, handlers, rexec

PRELUDE = -1
ADM = 0
INFO = 1
ACCOUNT = 2
PLUGIN = 3
GEMINI = 15



async def main():
    await bot.start()
    
    log.info("Бот запущен.")
    
    handlers.prelude.include(bot, PRELUDE)
    handlers.admin.include(bot, ADM)
    handlers.info.include(bot, INFO)
    handlers.plugins.include(bot, PLUGIN)
    handlers.gemini.include(bot, GEMINI)
    bot.add_handler(MessageHandler(handlers.gemini.gemini_ask, filters.mentioned | filters.private), group = GEMINI)
    
    log.info("Обработчики созданы.")
    
    await utils.db.initiate_admin(bot)
    await utils.bot.initiate_bot(bot)
    
    g.check_workers_job = g.scheduler.add_job(rexec.gWorkerManager.check_workers, 'interval', seconds=2)
    g.scheduler.start()
    
    g.bot_session = await bot.export_session_string()
    
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