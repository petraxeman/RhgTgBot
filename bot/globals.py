import os, toml, logging, asyncio
from pymongo import AsyncMongoClient, MongoClient



log = logging.getLogger("rhgTGBot:globals")



log.info("Загрузка конфигурации")
with open(os.path.join(".", "assets", "config.toml"), "r", encoding="utf8") as file:
    cfg = toml.loads(file.read())
cfg["SETTINGS"]["default_rights"] = cfg.get("SETTINGS", {}).get("default_rights", "")


log.info("Загрузка переменных")
sync_client = MongoClient(f'mongodb://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@{os.getenv("MONGO_DB_HOST")}:{os.getenv("MONGO_DB_PORT")}')
meta = sync_client.rhgtgbotdb.meta

variables = meta.find_one({"type": "global_variables"})
if not variables:
    meta.insert_one({
        "type": "global_variables",
        "hr_bot_name": os.getenv("TGBOT_HR_BOT_NAME"),
        "owner_username": os.getenv("TGBOT_OWNER_USERNAME"),
        "default_rights": os.getenv("TGBOT_DEFAULT_RIGHTS").replace(" ", "").split(",")
        })
variables = meta.find_one({"type": "global_variables"})

tg_bot_name = None
hr_bot_name = variables.get("tg_bot_name")
owner_username = variables.get("owner_username")
default_rights = variables.get("default_rights")

sync_client.close()


log.info("Загрузка базы данных")
client = AsyncMongoClient(f'mongodb://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@{os.getenv("MONGO_DB_HOST")}:{os.getenv("MONGO_DB_PORT")}')
#del os.environ["MONGO_DB_USER"]
#del os.environ["MONGO_DB_PASS"]
#del os.environ["MONGO_DB_HOST"]
#del os.environ["MONGO_DB_PORT"]
db = client.rhgtgbotdb
users = db.users
profiles = db.profiles
groups = db.groups

log.info("Загрузка закончена")