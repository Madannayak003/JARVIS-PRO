from core.registry import register
from voice.manager import speak

from skills.browser.browser_controller import browser


def ai_play(data):

    target = data.get("target","")

    if target == "first_result":

        speak("Playing first result")

        browser.play_first_video()

    else:

        browser.resume_video()

    return True


register("play", ai_play)