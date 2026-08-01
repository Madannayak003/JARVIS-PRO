from core.registry import register
from voice.manager import speak

from ai.ollama import ask_ollama

from core.paths import SCREENSHOTS

import os


def screenshot_ai(data):

    files = sorted(

        SCREENSHOTS.glob("*.png"),

        key=os.path.getmtime

    )

    if not files:

        speak("No screenshots found.")

        return True

    latest = files[-1]

    answer = ask_ollama(

        "Describe this screenshot.",

        str(latest)

    )

    speak(answer)

    return True


register(

    "screenshot_ai",

    screenshot_ai
)