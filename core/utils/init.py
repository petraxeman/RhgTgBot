from config import config
from depends.db import get_sync_db
from fastapi import FastAPI
from utils.db import create_user


def init_application(app: FastAPI):
    init_first_admin()
    init_app_args()


# TODO Добавить проверку на то что уже существует пользователь с all:full правами, а не только на username
def init_first_admin():
    if not config.BF_ADMIN_USERNAME:
        return None

    db = get_sync_db()
    user: dict | None = db.users.find_one({"username": config.BF_ADMIN_USERNAME})
    if user:
        return None
    new_admin = create_user(config.BF_ADMIN_USERNAME)
    new_admin["rights"] = ["all:full"]
    db.users.insert_one(new_admin)


def init_app_args():
    db = get_sync_db()
    args_map: dict | None = db.meta.find_one({"type": "global_variables"})

    if args_map is None:
        db.meta.insert_one({"type": "global_variables", "value": {"default_rights": config.BF_DEFAULT_RIGHTS}})
        return

    if not args_map.get("value", None):
        db.meta.update_one({"type": "global_variables"}, {"$set": {"default_rights": config.BF_DEFAULT_RIGHTS}})
