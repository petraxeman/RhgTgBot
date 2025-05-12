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

import utils, admin_handlers, info_handlers, gemini_handlers



PRELUDE = -1
ADM = 0
INFO = 1
ACCOUNT = 2
GEMINI = 3



async def pre_private_command(client: Client, message: Message):
    with g.db.transaction() as conn:
        try:
            user = conn.root.users[message.from_user.id]
        except KeyError:
            user = None
        
        if not user and g.register_mode == "auto":
            user = utils.db.User(message.from_user.username, message.from_user.id)
            conn.root.users[message.from_user.id] = user
        
        result = await utils.access.process(message.matches[0].group("command"), user.rights if user else [], message, log)

        message.sender_rights = list(user.rights)
    
    if not result:
        message.stop_propagation()


async def gemini_ask(client: Client, message: Message):
    if message.text[0] == "/":
        return
    userid = message.from_user.id
    task = asyncio.create_task(utils.send_typing(message))
    try:
        with g.db.transaction() as conn:
            try:
                user_rights = list(conn.root.users[userid].rights)
                profile_name = conn.root.users[userid].active_profile
                profile = conn.root.users[userid].profiles.get(profile_name)
                if profile:
                    token = profile.config.get("token")
                else:
                    token = None
            except KeyError:
                return
        
        if not token or len(token) < 20:
            return
        
        if message.chat.type == ChatType.PRIVATE:
            result = await utils.access.process("ask", user_rights, message, log)
            if not result:
                return
            await gemini_handlers.private_ask(client, message)
            
        elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            result = await utils.access.process("private_ask", user_rights, message, log)
            if not result:
                return
            await gemini_handlers.ask(client, message)
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
    
    bot.add_handler(MessageHandler(admin_handlers.add_user, filters.command("add_user") & filters.private), group = ADM)
    bot.add_handler(MessageHandler(admin_handlers.del_user, filters.command("del_user") & filters.private), group = ADM)
    bot.add_handler(MessageHandler(admin_handlers.users_list, filters.command("users_list") & filters.private), group = ADM)
    bot.add_handler(MessageHandler(admin_handlers.add_right, filters.command("add_right") & filters.private), group = ADM)
    bot.add_handler(MessageHandler(admin_handlers.sub_right, filters.command("sub_right") & filters.private), group = ADM)
    bot.add_handler(MessageHandler(admin_handlers.show_rights, filters.command("show_rights") & filters.private), group = ADM)
    bot.add_handler(MessageHandler(admin_handlers.app_args, filters.command("app_args") & filters.private), group = ADM)
    bot.add_handler(MessageHandler(admin_handlers.set_app_arg, filters.command("set_app_arg") & filters.private), group = ADM)
    
    bot.add_handler(MessageHandler(info_handlers.start_command, filters.command("start") & filters.private), group = INFO)
    bot.add_handler(MessageHandler(info_handlers.help_command, filters.command("help") & filters.private), group = INFO)
    
    bot.add_handler(MessageHandler(gemini_handlers.gmn_args, filters.command("gmn_args") & filters.private), group = GEMINI)
    bot.add_handler(MessageHandler(gemini_handlers.set_gmn_arg, filters.command("set_gmn_arg") & filters.private), group = GEMINI)
    bot.add_handler(MessageHandler(gemini_handlers.profiles, filters.command("profiles") & filters.private), group = GEMINI)
    bot.add_handler(MessageHandler(gemini_handlers.clone_profile, filters.command("clone_profile") & filters.private), group = GEMINI)
    bot.add_handler(MessageHandler(gemini_handlers.rename_profile, filters.command("rename_profile") & filters.private), group = GEMINI)
    bot.add_handler(MessageHandler(gemini_handlers.select_profile, filters.command("select_profile") & filters.private), group = GEMINI)
    bot.add_handler(MessageHandler(gemini_handlers.delete_profile, filters.command("delete_profile") & filters.private), group = GEMINI)
    
    bot.add_handler(MessageHandler(gemini_ask, filters.mentioned | filters.private), group = GEMINI)
    
    log.info("Обработчики созданы.")
    
    await utils.bot.initiate_admin(bot)
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
    
    utils.db.initiate_database(g.db)
    g.init_const()
    
    bot = utils.bot.setup_bot()
    
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    #uvloop.install()
    bot.run(main())