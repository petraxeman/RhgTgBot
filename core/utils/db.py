from uuid import uuid4

from config import config
from depends.db import get_sync_db


def create_user(username: str, uuid_provider: str | None = None, uuid: str | None = None):  # -> dict[str, Any]:
    uuid_dict = {"internal": uuid4().hex}
    if uuid_provider and uuid:
        uuid_dict[uuid_provider] = uuid
    db = get_sync_db()
    default_rights: list[str] = db[config.BF_MONGODB_DB].app.find_one({"type": "default_rights"}) or []
    return {
        "uuid": uuid_dict,
        "username": username,
        "rights": default_rights,
        "active_profile": "default",
        "profiles": ["default"],
        "is-baned": False
    }
