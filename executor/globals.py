import os



DB_CREDENTIALS = f'mongodb://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@{os.getenv("MONGO_DB_HOST")}:{os.getenv("MONGO_DB_PORT")}'
BOT_TOKEN = os.environ.get("BOT_TOKEN")