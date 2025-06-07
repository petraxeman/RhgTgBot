from pyrogram import Client
from pyrogram.types import Message

import utils, os, git
import globals as g
from . import asembly
import logging

log = logging.getLogger("rhgTGBot:plugins:update")


async def update(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Неправильные аргументы.")
        return
    
    plugin = await g.plugins.find_one({"codename": message.command[1]}, {"_id": 0})
    if not plugin:
        await message.reply_text("Такого плагина не существует.")
        return
    plugin = dict(plugin)
    
    with utils.temp.context_temp_dir() as dirname:
        temp_dir = os.path.join(".", "assets", "temp", dirname)
        git.Repo.clone_from(plugin["url"], temp_dir)
        raw_plugin = asembly.asembly("", temp_dir)
        await _process(plugin, raw_plugin)
    
    await message.reply_text(f"Плагин {plugin['codename']} успешно обновлен.")


async def _process(plugin: dict, raw_plugin: tuple):
    log.info(repr(raw_plugin))
    rp, rb, rt, rc = raw_plugin

    #buckets = await g.buckets.find({"plugin": plugin["codename"]})
        
    plugin["name"] = rp.get("name", "Unnamed plugin")
    plugin["description"] = rp.get("description", "")
    
    await _update_code(rc)
    await reinit_preloaded_code()
    

async def reinit_preloaded_code():
    g.preloaded_code = {}
    code_objs = g.code.find({})
    
    for code_obj in code_objs:
        if not g.preloaded_code.get(code_obj["plugin"]):
            g.preloaded_code[code_obj["plugin"]] = {}
        g.preloaded_code[code_obj["plugin"]][{code_obj["module"]}] = code_obj["code"]


async def _update_code(rc: list):
    for rcm in rc:
        ccm = await g.code.find_one({"plugin": rcm["plugin"], "module": rcm["module"]})
        if not ccm:
            await g.code.insert_one(rcm)
            continue
        
        if ccm["code"]:
            if ccm["code"] != rcm["code"]:
                await g.code.update_one({"plugin": rcm["plugin"], "module": rcm["module"]}, {"$set": {"code": rcm["code"]}})
            continue
        
        await g.code.delete_one({"plugin": rcm["plugin"], "module": rcm["module"]})