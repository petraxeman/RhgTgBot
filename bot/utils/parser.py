import re

from pyrogram.types import Message


command_word = r"^!([A-Za-z_][A-Za-z0-9_\-\.]+)\s*"
default_arg = r"^([A-Za-z0-9_\-\.]+)\s*"
string_arg = r'^("(?:\\.|[^\\"])+")'


def parse_command(command: str) -> list:
    cmd = []
    idx = 0

    if c := re.search(command_word, command[idx:]):
        cmd.append(c.group(1))
        idx += c.end()
    else:
        return []

    timeout = 0
    while True:
        if c := re.search(default_arg, command[idx:]):
            cmd.append(c.group(1))
            idx += c.end()
        elif c := re.search(string_arg, command[idx:]):
            cmd.append(c.group(1))
            idx += c.end()
        else:
            return cmd
        timeout += 1
        if timeout > 20:
            return []


def dump_message(message: Message):
    return {
        "sender": message.from_user.id,
        "chat_id": message.chat.id,
        "text": message.text
    }
