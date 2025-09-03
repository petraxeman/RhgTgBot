import globals as g


class UsersLib:
    def __init__(self, sender: dict):
        self.__current_user = sender
    
    def get_current_user(self):
        return self.__current_user
    
    async def get_user(self, username: str):
        if user := await g.users.find_one({"username": username}, {"username": 1, "tgid": 1}):
            return user
        return {}