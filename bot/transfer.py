import ZODB, os
from pymongo import MongoClient


# def parse_profiles(profiles):
#     new_profiles = {}
#     profiles = dict(profiles)
#     for profile in profiles.keys():
#         new_profiles[profile] = {
#             "chat": list(profiles[profile].chat),
#             "config": dict(profiles[profile].config)
#         }
#     return new_profiles

client = MongoClient(f'mongodb://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@{os.getenv("MONGO_DB_HOST")}:{os.getenv("MONGO_DB_PORT")}')
db = ZODB.DB("./assets/db/db.db")
mdb = client.rhgtgbotdb
users = mdb.users
profiles_coll = mdb.profiles
groups = mdb.groups

users.drop()
profiles_coll.drop()

with db.transaction() as conn:
    for tgid in conn.root.users:
        user = conn.root.users[tgid]
        profiles = user['profiles']
        user['profiles'] = list(profiles.keys())
        user['type'] = 'user'
        users.insert_one(user)
        
        for profile in profiles:
            print(user["username"], profiles[profile].get("chat"))
            newp = {
                "name": profile,
                "owner": user['tgid'],
                "config": {
                    "token": profiles[profile].get('token', ''),
                    "forgot": profiles[profile].get('forgot', False),
                    "search": profiles[profile].get('search', False),
                    "delete": profiles[profile].get('delete', False),
                    "skipmsg": profiles[profile].get('skipmsg', False),
                    "model": profiles[profile].get('model', "gemini-2.0-flash"),
                    "max_chat_size": profiles[profile].get('max_chat_size', 15),
                    "system_instruction": profiles[profile].get('system_instruction', "")
                },
                "chat": list(profiles[profile].get("chat", []))
            }
            print(newp)
            profiles_coll.insert_one(newp)

# {"default": {
#     "token": "",
#     "forgot": False,
#     "search": False,
#     "delete": False,
#     "skipmsg": False,
#     "model": "gemini-2.0-flash",
#     "max_chat_size": 15,
#     "system_instruction": system_instruction
# }}
    
# {
#     "name": "default",
#     "owner": tgid,
#     "config": {
#         "token": "",
#         "forgot": False,
#         "search": False,
#         "delete": False,
#         "skipmsg": False,
#         "model": "gemini-2.0-flash",
#         "max_chat_size": 15,
#         "system_instruction": system_instruction,
#     },
#     "chat": []
# }
        # conn.root.users[str(tgid)] = conn.root.old_users[tgid]

# users = []
# with db.transaction() as conn:
#     for tgid in conn.root.users.keys():
#         user = conn.root.users[tgid]
        
#         try:
#             username = user.username
#         except:
#             username = user.tgid
        
#         users.append( {
#             "username": username,
#             "tgid": tgid,
#             "rights": list(user.rights),
#             "active_profile": user.active_profile,
#             "profiles": parse_profiles(user.profiles)
#             }
#         )

# with db.transaction() as conn:
#     for user in users:
#         conn.root.users[user["tgid"]] = user
