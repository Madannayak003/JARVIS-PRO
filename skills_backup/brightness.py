import screen_brightness_control as sbc

from core.registry import register
from voice.manager import speak


def brightness(data):

    direction = data.get("direction", "up")

    current = sbc.get_brightness()[0]

    if direction == "up":

        sbc.set_brightness(min(100, current + 10))

        speak("Brightness increased")

    elif direction == "down":

        sbc.set_brightness(max(0, current - 10))

        speak("Brightness decreased")

    return True


register("brightness", brightness)