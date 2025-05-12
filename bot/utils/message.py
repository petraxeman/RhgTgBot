import re
import globals as g
from . import xor



def parse_ask_msg(text: str):
    regex = f"(?P<full_command>{g.tg_bot_name}[!/#]?(?P<flags>[fsdn012]+)?(?P<vector>=?[+-~]\\d*)?)"
    match = re.match(regex, text)
    
    flags = ""
    vector = ""
    clear_msg = text
    if match:
        flags = match.group("flags")
        vector = match.group("vector")
        clear_msg = text.replace(match.group("full_command"), g.hr_bot_name)
    
    flags = set(flags) if flags else set()
    vector = parse_vector(vector) if vector else {}
    return flags, vector, clear_msg


def parse_vector(direction: str):
    match = re.match(r"(?P<exact>=)?(?P<vector>[+-~])(?P<count>\d+)?", direction)
    data = {}
    data["strict"] = True if match.group("exact") else False

    match match.group("vector"):
        case "+":
            data["vector"] = -1
        case "-":
            data["vector"] = 1
        case "~":
            data["vector"] = 0
    
    try:
        data["count"] = int(match.group("count"))
        if data["count"] > 300:
            data["count"] = 300
        elif data["count"] < 1:
            data["count"] = 1
    except:
        data["count"] = 10
    
    return data


def parse_flags(flags: str, params: dict):
    new_params = {"token": params.get("token")}
    flags = set(flags)
    
    new_params["forgot"] = True if xor("f" in flags, params.get("forgot", False)) else False
    new_params["search"] = True if xor("s" in flags, params.get("search", False)) else False
    new_params["delete"] = True if xor("d" in flags, params.get("delete", False)) else False
    new_params["skip_msg"] = True if xor("n" in flags, params.get("skipmsg", False)) else False
    new_params["system_instruction"] = params.get("system_instruction", "")
    new_params["max_chat_size"] = params.get("max_chat_size", 15)
    
    if "0" in flags: new_params["model"] = "gemini-1.5-flash"
    elif "1" in flags: new_params["model"] = "gemini-2.0-flash"
    elif "2" in flags: new_params["model"] = "gemini-2.5-flash-preview-04-17"
    elif params.get("model"): new_params["model"] = params.get("model")
    else: new_params["model"] = "gemini-2.0-flash"
    
    return new_params