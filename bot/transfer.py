import ZODB, os
from pymongo import MongoClient


# def parse_profiles(profiles):
#     new_profiles = {}
#     profiles = dict(profiles)
#     for profile in profiles.keys():
#         new_profiles[profile] = {
#             "chat": list(profiles[profile].chat),
#             "config": dict(profiles[profile].config)
#         }
#     return new_profiles

client = MongoClient(f'mongodb://{os.getenv("MONGO_DB_USER")}:{os.getenv("MONGO_DB_PASS")}@{os.getenv("MONGO_DB_HOST")}:{os.getenv("MONGO_DB_PORT")}')
db = ZODB.DB("./assets/db/db.db")
mdb = client.rhgtgbotdb
users = mdb.users
profiles_coll = mdb.profiles
groups = mdb.groups

users.drop()
profiles_coll.drop()

with db.transaction() as conn:
    for tgid in conn.root.users:
        user = conn.root.users[tgid]
        profiles = user['profiles']
        user['profiles'] = list(profiles.keys())
        user['type'] = 'user'
        users.insert_one(user)
        
        for profile in profiles:
            print(user["username"], profiles[profile].get("chat"))
            newp = {
                "name": profile,
                "owner": user['tgid'],
                "config": {
                    "token": profiles[profile].get("config", {}).get('token', ''),
                    "forgot": profiles[profile].get("config", {}).get('forgot', False),
                    "search": profiles[profile].get("config", {}).get('search', False),
                    "delete": profiles[profile].get("config", {}).get('delete', False),
                    "skipmsg": profiles[profile].get("config", {}).get('skipmsg', False),
                    "model": profiles[profile].get("config", {}).get('model', "gemini-2.0-flash"),
                    "max_chat_size": profiles[profile].get("config", {}).get('max_chat_size', 15),
                    "system_instruction": profiles[profile].get("config", {}).get('system_instruction', "")
                },
                "chat": list(profiles[profile].get("chat", []))
            }
            print(newp)
            profiles_coll.insert_one(newp)

"""

import asyncio
import multiprocessing
import time
import os # Для получения PID

# --- Код для функции-потребителя ---
def consumer_worker(task_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):
    Целевая функция для каждого процесса-потребителя.
    Читает задачи из task_queue и отправляет результаты в result_queue.
    pid = os.getpid()
    print(f"Потребительский процесс {pid} запущен.")

    while True:
        try:
            # Ждем задачу. Блокирует ТОЛЬКО этот процесс.
            # Если очередь пуста, процесс простаивает.
            task = task_queue.get()
            print(f"Потребитель {pid} получил задачу: {task}")

            # Специальное значение для завершения процесса
            if task is None:
                print(f"Потребитель {pid} получил сигнал завершения. Выход.")
                break

            # --- Выполнение задачи ---
            # Здесь может быть любая блокирующая или CPU-интенсивная логика
            print(f"Потребитель {pid} выполняет задачу...")
            time.sleep(random.uniform(0.5, 2.0)) # Имитация разной продолжительности работы
            result = f"Результат от {pid} для задачи '{task}'"
            # --- Конец выполнения задачи ---

            # Отправляем результат обратно (если нужно)
            result_queue.put(result)
            print(f"Потребитель {pid} отправил результат.")

        except Exception as e:
            print(f"Ошибка в потребителе {pid}: {e}")
            # Можно отправить информацию об ошибке обратно в result_queue
            result_queue.put(f"Ошибка в потребителе {pid}: {e}")

# --- Код для основного asyncio процесса (Производитель)

async def main():
    # Создаем очереди для обмена данными
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    # Количество потребительских процессов, которые мы хотим запустить
    num_consumers = 3 # Например, 3 рабочих процесса

    # Список для хранения объектов процессов
    consumer_processes = []

    # Создаем и запускаем потребительские процессы
    print(f"Запуск {num_consumers} потребительских процессов...")
    for _ in range(num_consumers):
        process = multiprocessing.Process(target=consumer_worker, args=(task_queue, result_queue))
        process.start()
        consumer_processes.append(process)
        print(f"Запущен потребитель с PID: {process.pid}")

    # Получаем текущий цикл событий asyncio
    loop = asyncio.get_event_loop()

    # Корутина для получения результатов из потребительских процессов
    async def consume_results(result_queue: multiprocessing.Queue):
        print("Корутина ожидания результатов запущена...")
        # Ожидаем, пока все процессы живы ИЛИ пока очередь не пуста
        # (Могут быть результаты, отправленные перед завершением)
        while any(p.is_alive() for p in consumer_processes) or not result_queue.empty():
            try:
                # Ждем получения результата, не блокируя основной цикл
                result = await loop.run_in_executor(
                    None, # Используем ThreadPoolExecutor по умолчанию
                    result_queue.get
                )
                print(f"Основной процесс получил результат: {result}")
            except Exception as e:
                 # Если очередь пустеет и процессы завершены, get может вызвать ошибку
                 # или просто выход из цикла, если while условие изменилось.
                 # Можно добавить таймаут к get, если нужно более гранулярное управление.
                 print(f"Ошибка при получении результата или завершение: {e}")
                 break # Выход из цикла получения результатов

        print("Корутина ожидания результатов завершена.")


    # Запускаем корутину ожидания результатов в фоновом режиме asyncio
    results_consumer_task = asyncio.create_task(consume_results(result_queue))

    # - Логика производителя: отправка задач -
    print("Отправка задач в очередь...")
    tasks_to_send = [f"Задача {i}" for i in range(15)] # Например, 15 задач

    for task_data in tasks_to_send:
        # Отправляем задачу, используя run_in_executor, чтобы не блокировать main loop
        await loop.run_in_executor(
            None, # Используем ThreadPoolExecutor по умолчанию
            task_queue.put, task_data
        )
        print(f"Основной процесс отправил задачу: {task_data}")
        # Небольшая пауза для имитации асинхронной работы производителя
        await asyncio.sleep(0.1)

    # - Логика завершения работы: отправка сигналов потребителям -
    print(f"Отправка {num_consumers} сигналов завершения потребителям...")
    for _ in range(num_consumers):
        await loop.run_in_executor(None, task_queue.put, None) # Отправляем None для каждого процесса

    # - Ожидание завершения -
    print("Ожидание завершения всех потребительских процессов...")
    for process in consumer_processes:
        process.join() # Ждем, пока каждый процесс завершится
        print(f"Потребительский процесс {process.pid} завершен.")

    # Ждем, пока корутина consume_results получит оставшиеся результаты
    # Используем wait_for, чтобы не ждать бесконечно, если что-то пошло не так
    try:
        await asyncio.wait_for(results_consumer_task, timeout=5.0) # Даем немного времени на обработку остатков
    except asyncio.TimeoutError:
        print("Таймаут ожидания завершения корутины получения результатов. Возможно, остались необработанные результаты.")

    print("Основной процесс завершен.")

if __name__ == "main":
    # Важно: В Windows multiprocessing требует, чтобы запуск происходил внутри if name == "main":
    # Также, в Windows иногда могут быть проблемы с запуском процессов в IDE,
    # лучше запускать из командной строки.

import random # Импортируем здесь, чтобы worker_process_target мог его использовать
asyncio.run(main())"""