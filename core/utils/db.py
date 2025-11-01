from uuid import uuid4

from depends.db import get_sync_db


def create_user(username: str, uuid_provider: str | None = None, uuid: str | None = None):  # -> dict[str, Any]:
    uuid_dict = {"internal": uuid4().hex}
    if uuid_provider and uuid:
        uuid_dict[uuid_provider] = uuid
    default_rights: list[str] = get_sync_db().app.find_one({"type": "default_rights"}) or []
    return {
        "uuid": uuid_dict,
        "username": username,
        "rights": default_rights,
        "active_profile": "default",
        "profiles": ["default"],
        "is-baned": False
    }
