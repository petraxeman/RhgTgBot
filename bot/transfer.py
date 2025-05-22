import ZEO, ZODB, os, shutil
from BTrees.OOBTree import OOBTree



# def parse_profiles(profiles):
#     new_profiles = {}
#     profiles = dict(profiles)
#     for profile in profiles.keys():
#         new_profiles[profile] = {
#             "chat": list(profiles[profile].chat),
#             "config": dict(profiles[profile].config)
#         }
#     return new_profiles

client = ZEO.client(("127.0.0.1", 3000))
db = ZODB.DB(client)

with db.transaction() as conn:
    conn.root.old_users = conn.root.users
    conn.root.users = OOBTree()
    for tgid in conn.root.old_users.keys():
        conn.root.users[str(tgid)] = conn.root.old_users[tgid]
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
