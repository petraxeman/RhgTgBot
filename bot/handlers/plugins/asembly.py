import re, yaml, os
import logging

log = logging.getLogger("rhgTGBot:plugins:asembly")




def asembly(url: str, path: str) -> tuple:
    with open(os.path.join(path, "main.yml")) as file:
        data = yaml.safe_load(file)
    
    plugin = _parse_plugin(data.get("plugin", {}))
    if not plugin:
        return None, None, None, None
    
    plugin["url"] = url
    buckets = _parse_buckets(data.get("buckets", {}), plugin["codename"])
    triggers = _parse_triggers(data.get("triggers", {}))
    lua_code = _parse_lua_code(path, plugin["codename"])
    
    plugin["buckets"] = [b["codename"] for b in buckets]
    plugin["specific"] = triggers["specific"]
    plugin["commands"] = triggers["commands"]
    
    return plugin, buckets, triggers, lua_code


def _parse_lua_code(path: str, plugin_codename: dict):
    loaded_code = {}
    for root, dirs, files in os.walk(path):
        module = root.replace(path, "")
        module = module.replace("/", ".")
        
        for file in files:
            if file.endswith(".lua"):
                if module == "":
                    address = file[:-4]
                else:
                    address = module + "." + file[:-4]
                loaded_code[address] = open(os.path.join(root, file), "r").read()
    
    prepared_code = []
    for module in loaded_code:
        prepared_code.append({"module": module, "code": loaded_code[module], "plugin": plugin_codename})
    
    return prepared_code


def _parse_plugin(data: dict) -> dict:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]+", data.get("codename", "")):
        return {}
    return {"name": data["name"], "codename": data["codename"], "description": data.get("description", "")}


def _parse_buckets(buckets: list, plugin_codename: str) -> list[dict]:
    prepared_buckets = []
    for bucket in buckets:
        bucket.update({"type": "list", "access": "common", "encrypt": False})
        if codename := bucket.get("codename") and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]+", codename) and \
            bucket["access"] in ["common", "personal"] or \
            bucket["type"] in ["list", "dict"] or \
            bucket["encrypt"] in [True, False]:

            if codename == "rights":
                prepared_buckets.append({"plugin": plugin_codename, "codename": "rights", "type": "list", "access": "personal", "encrypt": False})
            else:
                prepared_buckets.append({"plugin": plugin_codename, "codename": codename, "type": bucket["type"], "encrypt": bucket["encrypt"], "access": bucket["access"]})
    return prepared_buckets


def _parse_triggers(data: dict) -> list[dict]:
    return {
        "specific": _parse_specific(data.get("specific", {})),
        "commands": _parse_commands(data.get("commands", {})),
        "shedules": _parse_schedules(data.get("schedules", {})),
        "ai_tools": _parse_ai_tools(data.get("ai_tools", {})),
        "api_endpoints": _parse_api_endpoints(data.get("api_endpoints", {}))
        }

def _parse_specific(specific: dict):
    return {
        "init": specific.get("init", None)
    }

def _parse_commands(commands: dict):
    prepared_commands = []
    
    for command in commands:
        facts = [isinstance(command["command"], str), isinstance(command["help"], str), isinstance(command["method"], str), isinstance(command.get("args", {}), dict),
                 re.fullmatch(r"[A-Za-z_][A-Za-z0-9_\-\.]+", command["method"]),]
        if False in facts:
            continue
        
        args = []; raw_args = command.get("args", {})
        for arg in raw_args:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_\.-]+", arg):
                continue
            if not raw_args[arg].get("t", None) in ["str", "int", "bool"]:
                continue
            
            args.append({"default": raw_args[arg].get("d", None), "type": raw_args[arg].get("t", None)})
            
        prepared_commands.append({"command": command["command"], "method": command["method"], "help": command["help"], "args": args})
    
    return prepared_commands

def _parse_schedules(schedules: dict):
    return []

def _parse_ai_tools(ai_tools: dict):
    return []

def _parse_api_endpoints(api_endpoints: dict):
    return []