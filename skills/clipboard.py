import pyperclip

from core.registry import register
from voice.manager import speak

from ai.ollama import ask_ollama


def clipboard(data):

    text = pyperclip.paste()

    mode = data.get("mode","read")

    if mode=="read":

        speak(text[:300])

        return True

    if mode=="summary":

        answer = ask_ollama(

            "Summarize this.",

            text

        )

        speak(answer)

        return True

    if mode=="explain":

        answer = ask_ollama(

            "Explain this.",

            text

        )

        speak(answer)

        return True

    return True


register("clipboard", clipboard)