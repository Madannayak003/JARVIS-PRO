import psutil

from core.registry import register
from voice.manager import speak

def battery(data):

    b = psutil.sensors_battery()

    if b:

        speak(f"Battery is {int(b.percent)} percent")

    else:

        speak("Battery information unavailable")

    return True


register("battery", battery)