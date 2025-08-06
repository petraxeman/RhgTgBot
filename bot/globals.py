import os, logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import AsyncMongoClient, MongoClient

log = logging.getLogger("rhgTGBot:globals")


_possible_gmn_models = {
    "gemma-3n-e2b-it": ["gemma-3n-e2b-it", "gemma-3n", "gemma"],
    "gemma-3n-e4b-it": ["gemma-3n-e4b-it"],
    "gemma-3-1b-it": ["gemma-3-1b-it"],
    "gemma-3-4b-it": ["gemma-3-4b-it"],
    "gemma-3-12b-it": ["gemma-3-12b-it"],
    "gemma-3-27b-it": ["gemma-3-27b-it", "gemma-3"],
    "gemini-2.0-flash": ["gemini-2.0-flash", "gemini-2.0", "gemini-2"],
    "gemini-2.0-flash-lite": ["gemini-2.0-flash-lite"],
    "gemini-2.5-pro": ["gemini-2.5-pro"],
    "gemini-2.5-flash": ["gemini-2.5-flash", "gemini-2.5", "gemini"],
    "gemini-2.5-flash-lite": ["gemini-2.5-flash-lite"]
}

POSSIBLE_GMN_MODELS = dict([(v, k) for k, v_list in _possible_gmn_models.items() for v in v_list])

GEMINI_ARGS = {
    "token": {"type": "string", "hide": True},
    "forgot": {"type": "bool"},
    "search": {"type": "bool"},
    "delete": {"type": "bool"},
    "skipmsg": {"type": "bool"},
    "model": {"type": "string", "variants": set(POSSIBLE_GMN_MODELS.keys()), "legend": POSSIBLE_GMN_MODELS},
    "max_chat_size": {"type": "int"},
    "system_instruction": {"type": "string", "long": True}   
}

del _possible_gmn_models


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