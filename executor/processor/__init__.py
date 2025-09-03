from . import worker_manager, general_worker



manager = worker_manager.WorkerManager(1, 1, general_worker.worker)

async def process(instruction: dict) -> any:
    manager.execute(instruction)