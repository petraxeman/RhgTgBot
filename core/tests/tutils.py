def create_user(rights: list[str] = ["gen:full", "gmn:full"]):
    return {
        "uuid": {"internal": "user"},
        "username": "user",
        "rights": rights,
        "active_profile": "default",
        "profiles": ["default"],
        "is-baned": False
    }


def create_admin():
    return {
        "uuid": {"internal": "admin"},
        "username": "admin",
        "rights": ["all:full"],
        "active_profile": "default",
        "profiles": ["default"],
        "is-baned": False
    }
