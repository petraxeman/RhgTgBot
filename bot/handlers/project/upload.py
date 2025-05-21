import logging
from pyrogram import Client
from pyrogram.types import Message
import globals as g
import utils, os, git, yaml, re, shutil

import utils.buckets

log = logging.getLogger("rhgTGBot:projects:projects")



async def upload_project(client: Client, message: Message):
    result = False
    log.info(message.command)
    if len(message.command) == 2 and message.command[1].endswith(".git"):
        with utils.tempdirs.context_temp_dir() as dirname:
            temp_dir = os.path.join(".", "assets", "temp", dirname)
            git.Repo.clone_from(message.command[1], temp_dir)
            result = _process(message.from_user, message.command[1], temp_dir)

    if not result:
        log.warning(f"Пользователь Пользователь {message.from_user.username} ({message.from_user.id}) хотел загрузить проект командой {repr(message.text)} но у него не получилось.")
        await message.reply_text("Что-то пошло не так...")
        return
    log.warning(f"Пользователь Пользователь {message.from_user.username} ({message.from_user.id}) загрузил свой проект командой {repr(message.text)}.")
    await message.reply_text("Проект загружен успешно.")


def _process(sender, url: str, path: str) -> bool:
    with open(os.path.join(path, "main.yml")) as file:
        data = yaml.safe_load(file)
        if not _verify(data):
            return False
        
        project_name = f"{sender.id}.{data["project"]['codename']}"

        # create buckets if they don't exists    
        bucket_names = [k for k in data["buckets"]]
        for bucket_name in bucket_names:
            bucket = data["buckets"][bucket_name]
            bucket["name"] = bucket_name
            utils.buckets.create_bucket(project_name, bucket)

        with g.db.transaction() as conn:
            conn.root.projects[project_name] = {
                "name": data["project"]["name"],
                "url": url,
                "buckets": bucket_names,
                "commands": []
            }
    
    try:
        os.makedirs(os.path.join("assets", "projects", project_name))
    except FileExistsError:
        shutil.rmtree(os.path.join("assets", "projects", project_name)) 
        os.makedirs(os.path.join("assets", "projects", project_name))

    for point in os.listdir(path):
        if point.endswith(".lua"):
            shutil.copy(os.path.join(path, point), os.path.join("assets", "projects", project_name))
    
    return True


def _verify(data: dict) -> bool:
    keys = list(data.get("project", {}).keys())
    if "name" not in keys or "codename" not in keys:
        return False
    
    if not re.fullmatch(r"[A-Za-z0-9\-_]+", data["project"]["codename"]): return False
    
    for bucket in data.get("buckets", []):
        bucket = data["buckets"][bucket]
        if bucket.get("access") not in ["common", "personal"]: return False
        if bucket.get("type") not in ["list", "dict"]: return False
        if bucket.get("encrypt") not in [True, False]: return False
    
    for trigger in data.get("triggers", []):
        template, command, args = trigger.split("$")
        if template.strip() not in ["cmd", "sch", "ait"]: return False
    
    return True