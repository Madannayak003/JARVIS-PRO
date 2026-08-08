import subprocess

from core.registry import register
from voice.manager import speak


def bluetooth_action(data):

    action = data.get("action")

    if action == "bluetooth_status":

        speak("Opening Bluetooth settings.")

        subprocess.Popen(
            "start ms-settings:bluetooth",
            shell=True
        )

        return True

    elif action == "bluetooth_devices":

        subprocess.Popen(
            "start ms-settings:bluetooth",
            shell=True
        )

        speak("Bluetooth settings opened.")

        return True

    return False


register("bluetooth_status", bluetooth_action)
register("bluetooth_devices", bluetooth_action)