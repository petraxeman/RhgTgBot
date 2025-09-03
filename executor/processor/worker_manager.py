import multiprocessing as mp
from uuid import uuid4
import asyncio
import logging
log = logging.getLogger()


class WorkerManager:
    def __init__(self, min_idle_wokers: int, max_idle_workers: int, method: callable):
        self.tasks_queue = mp.Queue()
        self.results_queue = mp.Queue()
        
        self.method = method
        
        self.min_idle_workers = min_idle_wokers or 1
        self.max_idle_workers = max_idle_workers or 10
        
        self.workers = {}
        
    def run_worker(self):
        uuid = str(uuid4())
        worker_obj = mp.Process(target=self.method, args=(self.tasks_queue, self.results_queue, uuid))
        self.workers[uuid] = {"worker": worker_obj, "state": "undefined"}
        worker_obj.start()
    
    async def execute(self, instruction: dict):
        idle_exists = False
        for uuid in self.workers:
            if self.workers[uuid]["state"] == "idle":
                idle_exists = True
                break

        if not idle_exists and len(self._workers) < self._max_idle_workers:
            self.run_worker()

        self.tasks_queue.put(instruction)
        log.info(f"Executor was called.")
        
        while True:
            r = self.results_queue.get()
            
            match r["type"]:
                case "worker_state":
                    self.workers[r["uuid"]]["state"] = r["state"]
                    log.info(f"Worker {r["uuid"]} set state to {r["state"]}")
                case "exception":
                    log.warning(f"Worker {r["uuid"]} raised exception: {r["message"]}")
                    self.workers[r["uuid"]]["state"] = "idle"
                    return
                case "result":
                    return r["value"]
    
