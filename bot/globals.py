import ZEO.asyncio
import ZEO.asyncio.client
import os, toml, ZODB, logging, ZEO

log = logging.getLogger("rhgTGBot:globals")

tg_bot_name = None
hr_bot_name = None
owner_username = None
default_rights = None
register_mode = None


log.info("Загрузка конфигурации")
with open(os.path.join(".", "assets", "config.toml"), "r", encoding="utf8") as file:
    cfg = toml.loads(file.read())


log.info("Загрузка базы данных")
client = ZEO.client(("127.0.0.1", 3000))
db = ZODB.DB(client)


def init_const():
    global owner_username, hr_bot_name, tg_bot_name, default_rights, register_mode
    with db.transaction() as conn:
        hr_bot_name = conn.root.config["hr_bot_name"]
        owner_username = conn.root.config["owner_username"]
        default_rights = conn.root.config["default_rights"]
        register_mode = conn.root.config["register_mode"]
    
    log.info(f"Загруженные имена - Owner:'{owner_username}', hr_bt:'{hr_bot_name}'")
    log.info(f"Загруженные права - '{default_rights}'")
    log.info(f"Режим регистрации - '{register_mode}'")