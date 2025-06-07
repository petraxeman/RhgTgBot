import os, logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import AsyncMongoClient, MongoClient

log = logging.getLogger("rhgTGBot:globals")



log.info("Загрузка переменных...")
db_credentials = f'mongodb://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@{os.getenv("MONGO_DB_HOST")}:{os.getenv("MONGO_DB_PORT")}'
del os.environ["MONGO_DB_USER"]
del os.environ["MONGO_DB_PASS"]
del os.environ["MONGO_DB_HOST"]
del os.environ["MONGO_DB_PORT"]

sync_client = MongoClient(db_credentials)
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
log.info("Переменные загружены.")


log.info("Загрузка кода плагинов...")

preloaded_code = {}
for code_obj in sync_client.rhgtgbotdb.code.find({}):
    if not preloaded_code.get(code_obj["plugin"]):
        preloaded_code[code_obj["plugin"]] = {}
    preloaded_code[code_obj["plugin"]][code_obj["module"]] = code_obj["code"]

log.info("Загрузка кода плагинов закончена.")

sync_client.close()


log.info("Загрузка базы данных...")

client = AsyncMongoClient(db_credentials)

db = client.rhgtgbotdb

users = db.users
profiles = db.profiles
groups = db.groups
plugins = db.plugins
buckets = db.buckets
code = db.code

log.info("Загрузка закончена.")


log.info("Создание планироващика...")
scheduler = AsyncIOScheduler()
log.info("Планировщик создан.")