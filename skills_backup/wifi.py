import subprocess

from core.registry import register
from voice.manager import speak


def wifi_action(data):

    action = data.get("action")

    # ----------------------------
    # Turn Wi-Fi ON
    # ----------------------------
    if action == "wifi_on":

        subprocess.run(
            'netsh interface set interface "Wi-Fi" enable',
            shell=True
        )

        speak("Wi-Fi turned on.")

        return True

    # ----------------------------
    # Turn Wi-Fi OFF
    # ----------------------------
    elif action == "wifi_off":

        subprocess.run(
            'netsh interface set interface "Wi-Fi" disable',
            shell=True
        )

        speak("Wi-Fi turned off.")

        return True

    # ----------------------------
    # Wi-Fi Status
    # ----------------------------
    elif action == "wifi_status":

        result = subprocess.run(
            "netsh wlan show interfaces",
            capture_output=True,
            text=True,
            shell=True
        )

        output = result.stdout

        if "connected" in output.lower():

            speak("Wi-Fi is connected.")

        else:

            speak("Wi-Fi is not connected.")

        return True

    # ----------------------------
    # List Networks
    # ----------------------------
    elif action == "wifi_list":

        result = subprocess.run(
            "netsh wlan show networks",
            capture_output=True,
            text=True,
            shell=True
        )

        print(result.stdout)

        speak("Available Wi-Fi networks are displayed in the terminal.")

        return True

    return False


register("wifi_on", wifi_action)
register("wifi_off", wifi_action)
register("wifi_status", wifi_action)
register("wifi_list", wifi_action)