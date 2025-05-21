import persistent
import persistent.list
import persistent.mapping
import logging
import globals as g
import os

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
        if not hasattr(conn.root, "groups"): conn.root.groups = IOBTree()
        if not hasattr(conn.root, "projects"): conn.root.projects = OOBTree()
        if not hasattr(conn.root, "buckets"): conn.root.buckets = OOBTree()
        if not hasattr(conn.root, "config") or g.cfg.get("SETUP", {}).get("reload_config", False):
            conn.root.config = persistent.mapping.PersistentMapping()

            g.cfg["SETTINGS"]["owner_username"] = g.cfg.get("SETTINGS", {}).get("default_rights", "").replace(" ", "").split(",")
            set_if_not_exists(conn.root.config, g.cfg.get("SETUP", {}), "owner_username")
            for prop in g.cfg.get("SETTINGS", {}).keys():
                set_if_not_exists(conn.root.config, g.cfg.get("SETTINGS", {}), prop)


def initiate_derictories():
    for directory in ["assets", "logs"]:
        if not os.path.exists(os.path.join(".", directory)):
            os.makedirs(os.path.join(".", directory))
    
    for directory in ["db", "sessions", "temp", "projects"]:
        if not os.path.exists(os.path.join(".", "assets", directory)):
            os.makedirs(os.path.join(".", "assets", directory))


def validate_db():
    with g.db.transaction() as conn:
        for user in conn.root.users.keys():
            pass


class User(persistent.Persistent):
    def __init__(self, username, tgid):
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
