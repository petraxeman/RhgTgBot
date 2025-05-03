import os
import globals as g

access_rights = {
    # Administration category
    ## Users section
    "add_user": {"adm:add_user", "adm:gr:users", "adm:full"},
    "del_user": {"adm:del_user", "adm:gr:users", "adm:full"},
    "users_list": {"adm:users_list", "adm:gr:users", "adm:full"},
    ## App settings section
    "app_args": {"adm:app_args", "adm:gr:app", "adm:full"},
    "set_app_arg": {"adm:set_app_arg", "adm:gr:app", "adm:full"},
    ## Rights section
    "add_right": {"adm:add_right", "adm:gr:rights", "adm:full"},
    "sub_right": {"adm:sub_right", "adm:gr:rights", "adm:full"},
    "show_rights": {"adm:show_rights", "adm:show_self_rights", "adm:gr:rights", "adm:full"},
    ## App settings
    "app_args": {"adm:app_args", "adm:gr:app", "adm:full"},
    "set_app_arg": {"adm:set_app_arg", "adm:gr:app", "adm:full"},
    
    # Gemini category
    ## Settings section
    "gmn_args": {"gmn:gmn_args", "gmn:gr:settings", "gmn:full"},
    "set_gmn_arg": {"gmn:set_gmn_arg", "gmn:gr:settings", "gmn:full"},
    ## Profiles section
    "profiles": {"gmn:profiles", "gmn:gr:profiles", "gmn:full"},
    "clone_profile": {"gmn:clone_profile", "gmn:gr:profiles", "gmn:full"},
    "select_profile": {"gmn:select_profile", "gmn:gr:profiles", "gmn:full"},
    "rename_profile": {"gmn:rename_profile", "gmn:gr:profiles", "gmn:full"},
    ## Talking with gemini
    "ask": {"gmn:ask", "gmn:gr:talking", "gmn:full"},
    "private_ask": {"gmn:private_ask", "gmn:gr:talking", "gmn:full"}
}



def verify(method: str, user_rights: list) -> bool:
    if set(access_rights.get(method, set())).intersection(user_rights) or "all:full" in user_rights:
        return True
    else:
        return False


async def process(method, user_rights, message, log):
    if not verify(method, user_rights) and message.from_user.username != g.owner_username:
        log.warning(f"Пользователь {message.from_user.username} ({message.from_user.id}) пытался вызвать метод /{method} без прав.")
        return False
    else:
        return True