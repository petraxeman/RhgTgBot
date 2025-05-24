import logging
import globals as g
import os

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