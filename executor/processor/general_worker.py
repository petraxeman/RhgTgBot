import multiprocessing as mp
import traceback
from pymongo import MongoClient
from origamibot import OrigamiBot as Bot
import globals as g
import lupa

from . import (
    sx_bucket,
    sx_telegram,
    sx_users
)

class Importer:
    def __init__(self, message: dict, plugin: str, module: str, method: str, tg_client, db):
        self._message = message
        self._plugin = plugin
        self._module = module
        self._method = method
        self._client = tg_client
        self._db = db
    
    def __call__(self, m: str):
        match m:
            case "rp:Telegram":
                return sx_telegram.Library(self._client, self._message)
            case "rp:Buckets":
                return sx_bucket.Library(self._db, self._plugin, self._message.get("user_id"))


def worker(tasks: mp.Queue, result: mp.Queue, uuid: str, type: str = "idle"):
    result.put({"type": "worker_state", "wuid": uuid, "state": "starting"})
    
    db = MongoClient(g.DB_CREDENTIALS)
    tg = Bot(g.BOT_TOKEN)
    uuid = uuid
    tasks_queue = tasks
    results_queue = result
    
    results_queue.put({"type": "worker_state", "wuid": uuid, "state": "idle"})
    
    while True:
        task = tasks_queue.get()
        
        results_queue.put({"type": "worker_state", "wuid": uuid, "state": "busy"})
        
        try:
            match task["type"]:
                case "execute_command":
                    command_executor(task, db, tg)
                case "intall_plugin":
                    plugin_installer()
            
            raise Exception(f"Undefined task type - {task["type"]}")
        except Exception as e:
            results_queue.put({"type": "exception", "wuid": uuid, "message": str(e) + "   " + str(traceback.format_exc())})


def command_executor(task: dict, db: MongoClient, tg_client: Bot):
    message = task["message"]; plugin = task["plugin"]; method = task["method"]; command = task["command"]
    module = ".".join(method.split(".")[:-1])
    method = method.split(".")[-1]
    
    loaded_code = db.sxassistant.code.find_one({"plugin": plugin["codename"], "module": module})
    if not loaded_code:
        return
    
    lua = lupa.LuaRuntime()
    lua.globals()["import"] = Importer(message, plugin, module, method, tg_client, db.sxassistant)
    lua.execute(loaded_code["code"])
    lua.globals()[method](*command[1:])


def filter_attribute_access(obj, attr_name, is_setting):
    if isinstance(attr_name, str):
        if not attr_name.startswith('_'):
            return attr_name
    raise Exception("Access denied")


def plugin_installer():
    pass