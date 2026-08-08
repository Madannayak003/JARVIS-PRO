import psutil

from core.registry import register
from voice.manager import speak


def taskmanager(data):

    cpu = psutil.cpu_percent()

    ram = psutil.virtual_memory().percent

    disk = psutil.disk_usage("/").percent

    print()

    print("CPU :", cpu)

    print("RAM :", ram)

    print("Disk:", disk)

    print()

    speak(

        f"CPU {cpu} percent. "

        f"RAM {ram} percent."

    )

    return True


register("taskmanager", taskmanager)