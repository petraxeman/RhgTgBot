import ZEO, ZODB, os, shutil



def parse_profiles(profiles):
    new_profiles = {}
    profiles = dict(profiles)
    for profile in profiles.keys():
        new_profiles[profile] = {
            "chat": list(profiles[profile].chat),
            "config": dict(profiles[profile].config)
        }
    return new_profiles

client = ZEO.client(("127.0.0.1", 3000))
db = ZODB.DB(client)

users = []
with db.transaction() as conn:
    for tgid in conn.root.users.keys():
        user = conn.root.users[tgid]
        users.append( {
            "tgid": tgid,
            "rights": list(user.rights),
            "active_profile": user.active_profile,
            "profiles": parse_profiles(user.profiles)
            }
        )

for user in users:
    print(user["tgid"])
    print(user)
    print("\n\n\n")