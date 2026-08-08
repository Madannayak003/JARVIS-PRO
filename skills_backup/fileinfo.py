import os
import datetime

from core.registry import register
from voice.manager import speak


def info(data):

    path = data["path"]

    size = os.path.getsize(path)

    modified = datetime.datetime.fromtimestamp(

        os.path.getmtime(path)

    )

    print()

    print("File :", path)

    print("Size :", size)

    print("Modified :", modified)

    print()

    speak("File information printed.")

    return True


register(
    "file_info",
    info
)