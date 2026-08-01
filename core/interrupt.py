"""
Interrupt Engine

Stops whatever JARVIS is doing.
"""

from voice.player import stop
from voice.manager import stop_speaking
from core.task_manager import task_manager
from core.command_queue import clear
from core.busy_manager import finish_task

import time

def interrupt():

    print("[INTERRUPT]")

    stop()

    stop_speaking()

    clear()

    task_manager.stop_all()

    time.sleep(0.1)

    print("[INTERRUPT COMPLETE]")
    
    finish_task()