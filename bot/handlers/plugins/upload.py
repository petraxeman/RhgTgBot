import logging
from pyrogram import Client
from pyrogram.types import Message

import rexec
from . import follow, asembly
import globals as g
import utils, os, git, yaml, re

log = logging.getLogger("rhgTGBot:plugins:upload")



async def upload_plugin(client: Client, message: Message):
    result = False
    if len(message.command) == 2 and message.command[1].endswith(".git"):
        if await g.plugins.find_one({"url": message.command[1]}):
            await message.reply_text("Такой проект уже загружен")
        
        with utils.temp.context_temp_dir() as dirname:
            temp_dir = os.path.join(".", "assets", "temp", dirname)
            git.Repo.clone_from(message.command[1], temp_dir)
            result = await _process(message.from_user, message.command[1], temp_dir)

    if not result:
        log.warning(f"Пользователь Пользователь {message.from_user.username} ({message.from_user.id}) хотел загрузить проект командой {repr(message.text)} но у него не получилось.")
        await message.reply_text("Что-то пошло не так...")
        return
    
    log.warning(f"Пользователь Пользователь {message.from_user.username} ({message.from_user.id}) загрузил проект командой {repr(message.text)}.")
    await message.reply_text("Проект загружен успешно.")
    message.command = ["follow", result["codename"]]
    await follow.follow(client, message)
    
    if result["specific"].get("init"):
        await rexec.gWorkerManager.execute_command(message.sender, result["codename"], result["specific"]["init"], [])


async def _process(url: str, path: str) -> bool:
    plugin, buckets, triggers, code = asembly.asembly(url, path)
    plugin["url"] = url
    
    log.info(repr(triggers))
    
    await g.plugins.insert_one(plugin)
    if buckets: await g.buckets.insert_many(buckets)
    if code: await g.code.insert_many(code)
                
    return plugin


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
    parsed_commands = []
    
    for command in commands:
        if not isinstance(command["command"], str) or not isinstance(command["help"], str):
            continue
        
        if not isinstance(command["method"], str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_\-\.]+", command["method"]):
            continue
        
        if not isinstance(command.get("args", {}), dict):
            continue
        
        args = []
        for arg in command.get("args", {}):
            if ":" in command["args"][arg]:
                value_default, value_type = command["args"][arg].split(":")
            else:
                value_default = None; value_type = command["args"][arg]
            
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_\.-]+", arg):
                continue
            
            if not value_type in ["str", "int", "bool"]:
                continue
            
            args.append({"default": value_default, "type": value_type})
            
        parsed_commands.append({
            "command": command["command"],
            "method": command["method"],
            "help": command["help"],
            "args": args
            })
    
    return parsed_commands


def _parse_schedules(schedules: dict):
    return []

def _parse_ai_tools(ai_tools: dict):
    return []

def _parse_api_endpoints(api_endpoints: dict):
    return []