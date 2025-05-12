import persistent
import persistent.list
import persistent.mapping
import logging
import globals as g

import ZODB
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree

log = logging.getLogger("rhgTGBot:dbsetup")

system_instruction = ""
actual_version = 1



def initiate_database(db):
    def set_if_not_exists(config, cfg, name):
        config[name] = cfg.get(name, "") if not config.get(name) else config[name]
        
    with db.transaction() as conn:
        if not hasattr(conn.root, "users"): conn.root.users = IOBTree()
        if not hasattr(conn.root, "users_list"): conn.root.users_list = persistent.list.PersistentList()
        if not hasattr(conn.root, "groups"): conn.root.buckets = IOBTree()
        if not hasattr(conn.root, "buckets"): conn.root.buckets = OOBTree()
        if not hasattr(conn.root, "config") or g.cfg.get("SETUP", {}).get("reload_config", False):
            conn.root.config = persistent.mapping.PersistentMapping()

            g.cfg["SETTINGS"]["owner_username"] = g.cfg.get("SETTINGS", {}).get("default_rights", "").replace(" ", "").split(",")
            set_if_not_exists(conn.root.config, g.cfg.get("SETUP", {}), "owner_username")
            for prop in g.cfg.get("SETTINGS", {}).keys():
                set_if_not_exists(conn.root.config, g.cfg.get("SETTINGS", {}), prop)


def validate():
    log.info("Начало миграции.")
    
    old_db = ZODB.DB("/bot/migration_from/db.db")
    tgids = []
    with old_db.transaction() as conn:
        tgids = list(conn.root.users.keys())
    
    for tgid in tgids:
        user = {}
        with old_db.transaction() as conn:
            u = conn.root.users[tgid]
            # For very old version
            if isinstance(u, persistent.mapping.PersistentMapping):
                user["username"] = u.get("tg_username")
                user["tgid"] = u.get("tg_id")
                user["rights"] = list(u.get("rights", g.default_rights))
                user["profile_config"] = dict(u.get("gemini_config", {}))
                user["profile_config"]["token"] = u.get("gemini_token", None)
                user["chat"] = list(u.get("chat"))
    
        with g.db.transaction() as conn:
            if user:
                u = User(user["username"], user["tgid"])
                u.rights = user["rights"]
                u.profiles["default"].chat = user["chat"]
                u.profiles["default"].config = user["profile_config"]
                conn.root.users[tgid] = u
    
    with old_db.transaction() as conn:
        for tgid in conn.root.users:
            user = conn.root.users[tgid]
            log.info(f"{tgid} {user.get('tg_username')}")
    
    with g.db.transaction() as conn:
        for tgid in conn.root.users:
            user = conn.root.users[tgid]
            log.info(f"{tgid} {user.username}")
    log.info("Миграция завершена.")


class User(persistent.Persistent):
    def __init__(self, username, tgid):
        self.version = 1
        self.username = username
        self.tgid = tgid
        self.rights = persistent.list.PersistentList()
        self.active_profile = "default"
        self.profiles = persistent.mapping.PersistentMapping({"default": PersonalBot()})


class PersonalBot(persistent.Persistent):
    def __init__(self):
        self.version = 1
        self.chat = []
        self.config = persistent.mapping.PersistentMapping({
            "token": None,
            "forgot": False,
            "search": False,
            "delete": False,
            "skipmsg": False,
            "model": "gemini-2.0-flash",
            "max_chat_size": 15,
            "system_instruction": system_instruction
            })


class TGGroup(persistent.Persistent):
    def __init__(self, tgid):
        self.tgid = tgid
        self.rules = persistent.mapping.PersistentMapping({
            "delete_timeout": -1
        })
        self.deletion_queue = persistent.list.PersistentList()


class Bucket(persistent.Persistent):
    def __init__(self, owner: int, name: str, is_dict: bool = False):
        self.owner = owner
        self.name  = name
        self.users = persistent.list.PersistentList()
        
        if is_dict:
            self.data  = persistent.mapping.PersistentMapping()
        else:
            self.data  = persistent.list.PersistentList()
