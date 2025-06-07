import lupa, uuid, os
import multiprocessing as mp
import globals as g
from pymongo import MongoClient

from origamibot import OrigamiBot as Bot

#from . import luaUsersLib, luaBucketsLib 
from . import rhgTelegramLib
from pyrogram.types import Message

import logging
log = logging.getLogger("rhgTGBot:worker_manager")


class Importer:
    def __init__(self, message: dict, plugin: str, module: str, method: str, tg_client):
        self.__message = message
        self.__plugin = plugin
        self.__module = module
        self.__method = method
        self.__client = tg_client
    
    def __call__(self, m: str):
        match m:
            case "py:Telegram":
                return rhgTelegramLib.TelegramLib(self.__client, self.__message)


class WorkerManager:
    def __init__(self, min_idle_wokers: int, max_idle_workers: int):
        self._tasks = mp.Queue()
        self._result = mp.Queue()
        self._min_idle_workers = min_idle_wokers or 1
        self._max_idle_workers = max_idle_workers or 10
        self._workers = {}
    
    def run_worker(self):
        wuid = str(uuid.uuid4())
        worker_obj = mp.Process(target=worker, args=(self._tasks, self._result, wuid))
        self._workers[wuid] = {"worker": worker_obj, "state": "undefined"}
        worker_obj.start()
    
    async def check_workers(self):
        while not self._result.empty():
            r = self._result.get()
            
            match r["type"]:
                case "worker_state":
                    self._workers[r["wuid"]]["state"] = r["state"]
                    log.info(f"Worker {r["wuid"]} set state to {r["state"]}")
                case "exception":
                    log.warning(f"Worker {r["wuid"]} raised exception: {r["message"]}")
        
    async def execute_command(self, message: Message, plugin: str, method: str, command: list):
        idle_exists = False
        for wuid in self._workers:
            if self._workers[wuid]["state"] == "idle":
                idle_exists = True
                break

        if not idle_exists and len(self._workers) < self._max_idle_workers:
            self.run_worker()
        
        self._tasks.put({"type": "execute_command", "message": message, "plugin": plugin, "method": method, "command": command})
        log.info(f"Была вызвана команда {command[0]} и обработана.")


def worker(tasks: mp.Queue, result: mp.Queue, wuid: str, type: str = "idle"):
    import traceback
    result.put({"type": "worker_state", "wuid": wuid, "state": "starting"})
    db = MongoClient(g.db_credentials)
    tg = Bot(g.BOT_TOKEN)
    wuid = wuid
    tq = tasks
    rq = result
    
    rq.put({"type": "worker_state", "wuid": wuid, "state": "idle"})
    
    while True:
        task = tq.get()
        
        rq.put({"type": "worker_state", "wuid": wuid, "state": "busy"})
        
        try:
            match task["type"]:
                case "execute_command":
                    command_executor(task, db, tg)

            rq.put({"type": "worker_state", "wuid": wuid, "state": "idle"})
        except Exception as e:
            rq.put({"type": "exception", "wuid": wuid, "message": str(e) + "   " + str(traceback.format_exc())})


# sender: dict, plugin: str, method: str, command: list
def command_executor(task: dict, db: MongoClient, tg_client: Bot):
    message = task["message"]; plugin = task["plugin"]; method = task["method"]; command = task["command"]
    module = ".".join(method.split(".")[:-1])
    method = method.split(".")[-1]
    
    loaded_code = db.rhgtgbotdb.code.find_one({"plugin": plugin["codename"], "module": module})
    if not loaded_code:
        return
    
    lua = lupa.LuaRuntime()
    lua.globals()["import"] = Importer(message, plugin, module, method, tg_client)
    lua.execute(loaded_code["code"])
    lua.globals()[method](*command[1:])


def filter_attribute_access(obj, attr_name, is_setting):
    if isinstance(attr_name, str):
        if not attr_name.startswith('_'):
            return attr_name
    raise Exception("Access denied")



gWorkerManager = WorkerManager(os.getenv("MIN_IDLE_WORKERS"), os.getenv("MAX_IDLE_WORKERS"))