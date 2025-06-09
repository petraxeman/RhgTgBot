import globals as g
from pyrogram import Client



class TelegramLib:
    def __init__(self, client: Client, message: dict):
        self._client = client
        self._message = message

    def send_text(self, chat_id: str, text: str):
        self._client.send_message(self, chat_id, text)
    
    def get_current_message(self):
        return CurrentMessage(self._client, self._message.get("chat_id"), self._message.get("text", ""))


class CurrentMessage:
    def __init__(self, client: Client, chat_id: int, message_text: str):
        self._client = client
        self._chat_id = chat_id
        self._message_text = message_text
    
    def reply_text(self, text: str):
        return self._client.send_message(self._chat_id, text)