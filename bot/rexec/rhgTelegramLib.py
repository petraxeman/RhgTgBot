import globals as g
from pyrogram import Client



class TelegramLib:
    def __init__(self, client: Client, message: dict):
        self.__client = client
        self.__message = message

    def get_current_message(self):
        return CurrentMessage(self.__client, self.__message.get("chat_id"), self.__message.get("text", ""))


class CurrentMessage:
    def __init__(self, client: Client, chat_id: int, message_text: str):
        self.__client = client
        self.__chat_id = chat_id
        self.__message_text = message_text
    
    def reply_text(self, text: str):
        return self.__client.send_message(self.__chat_id, text)