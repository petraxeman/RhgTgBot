import logging
import os

import globals as g


log = logging.getLogger("rhgTGBot:dbsetup")

system_instruction = ""


def initiate_derictories():
    for directory in ["assets", "logs"]:
        if not os.path.exists(os.path.join(".", directory)):
            os.makedirs(os.path.join(".", directory))

    for directory in ["db", "sessions", "temp", "projects"]:
        if not os.path.exists(os.path.join(".", "assets", directory)):
            os.makedirs(os.path.join(".", "assets", directory))


async def initiate_admin(client):
    log.info("Настройка админа.")
    user_info = await client.get_users(g.owner_username)
    admin = await g.users.find_one({"tgid": user_info.id})
    if not admin:
        user_object = create_user(user_info.id, user_info.username)
        user_object["rights"] = ["all:full"]
        await g.users.insert_one(user_object)

    default_admin_profile = await g.profiles.find_one({"owner": user_info.id})
    if not default_admin_profile:
        await g.profiles.insert_one(create_profile(user_info.id))


def create_user(tgid: int, username: str) -> dict:
    return {
        "type": "user",
        "tgid": tgid,
        "username": username,
        "rights": g.default_rights,
        "active_profile": "default",
        "available_commands": {},
        "profiles": ["default"]
    }


def create_profile(tgid: int) -> dict:
    return {
        "name": "default",
        "owner": tgid,
        "config": {
            "token": "",
            "forgot": False,
            "search": False,
            "delete": False,
            "skipmsg": False,
            "model": "gemini-2.0-flash",
            "max_chat_size": 15,
            "system_instruction": system_instruction,
        },
        "chat": []
    }


def create_plugin(owner: int,
                  name: str,
                  codename: str,
                  url: str,
                  access: str = "private"):
    return {
        "owner": owner,
        "name": name,
        "codename": codename,
        "url": url,
        "access": access,
        "followers": [],
        "buckets": [],
        "commands": []
    }


def create_bucket(plugin_codename: str,
                  bucket_codename: str,
                  bucket_type: str,
                  bucket_access: str,
                  encrypt: bool = False):
    bucket = {
        "plugin": plugin_codename,
        "codename": bucket_codename,
        "type": bucket_type,
        "access": bucket_access,
        "encrypt": encrypt
    }
    if bucket_type == "list":
        bucket["items"] = []
    elif bucket_type == "dict":
        bucket["items"] = {}

    return bucket
