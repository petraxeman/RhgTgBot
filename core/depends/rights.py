from depends.db import get_async_db
from fastapi import (
    Depends,
    HTTPException,
    Request,
    status
)
from pymongo.asynchronous.database import AsyncDatabase


RIGHTS_MAP = {
    # General category
    # Users section
    "get_public_user": {"gen:get_public_user", "gen:gr:users", "gen:full", "all:full"},
    # Administration category
    # Users section
    "add_user": {"adm:add_user", "adm:gr:users", "adm:full", "all:full"},
    "del_user": {"adm:del_user", "adm:gr:users", "adm:full", "all:full"},
    "get_user": {"adm:get_user", "adm:gr:users", "adm:full", "all:full"},
    "get_users_list": {"adm:users_list", "adm:gr:users", "adm:full", "all:full"},

    # App settings section
    "app_args": {"adm:app_args", "adm:gr:app", "adm:full", "all:full"},
    "set_app_arg": {"adm:set_app_arg", "adm:gr:app", "adm:full", "all:full"},

    # Rights section
    "add_rights": {"adm:add_rights", "adm:gr:rights", "adm:full", "all:full"},
    "del_rights": {"adm:del_rights", "adm:gr:rights", "adm:full", "all:full"},
    "get_rights": {"adm:get_rights", "adm:gr:rights", "adm:full", "all:full"},
    "get_self_rights": {"adm:get_self_rights", "adm:gr:rights", "adm:full", "all:full"},

    # Gemini category
    # Settings section
    "gmn_args": {"gmn:gmn_args", "gmn:gr:settings", "gmn:full", "all:full"},
    "set_gmn_arg": {"gmn:set_gmn_arg", "gmn:gr:settings", "gmn:full", "all:full"},
    # Profiles section
    "profiles": {"gmn:profiles", "gmn:gr:profiles", "gmn:full", "all:full"},
    "clone_profile": {"gmn:clone_profile", "gmn:gr:profiles", "gmn:full", "all:full"},
    "select_profile": {"gmn:select_profile", "gmn:gr:profiles", "gmn:full", "all:full"},
    "rename_profile": {"gmn:rename_profile", "gmn:gr:profiles", "gmn:full", "all:full"},
    # Talking with gemini
    "ask": {"gmn:ask", "gmn:gr:talking", "gmn:full", "all:full"},
    "private_ask": {"gmn:private_ask", "gmn:gr:talking", "gmn:full", "all:full"}
}


def verify_user(required_right: str):
    async def _verify_user(request: Request, db: AsyncDatabase = Depends(get_async_db)):
        request.state.data = await request.json()
        user: dict | None = await db.users.find_one({"uuid": {request.state.data.get("initiator")[0]: request.state.data.get("initiator")[1]}})
        if not user:
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, "User not found.")
        if set(RIGHTS_MAP.get(required_right, {})).intersection(set(user["rights"])):
            return user
        else:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You can't do this.")
    return _verify_user
