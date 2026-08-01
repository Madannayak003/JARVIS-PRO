import threading
import time

from core.task_queue import get_task
from core.task_queue import has_tasks

from core.registry import execute

running = True

def worker():

    while running:

        if has_tasks():

            task = get_task()

            action = task["action"]

            print(f"\n[TASK] {action}")

            print("Starting:", action)

            execute(action, task)

            print("Finished:", action)

        else:

            time.sleep(0.1)


def start_worker():

    threading.Thread(
        target=worker,
        daemon=True
    ).start()