import os
import ctypes

from core.registry import register
from voice.manager import speak
from core.confirmation import ask


def system_action(data):

    action = data.get("action")

    if action == "shutdown":

        if data.get("confirmed"):

            speak("Shutting down computer")

            os.system("shutdown /s /t 1")

        else:

            ask(
                "shutdown",
                {
                    "action":"shutdown",
                    "confirmed":True
                }
            )

            speak(
                "Are you sure you want to shut down your computer?"
            )

        return True

    elif action == "restart":

        if data.get("confirmed"):

            speak("Restarting computer")

            os.system("shutdown /r /t 1")

        else:

            ask(
                "restart",
                {
                    "action":"restart",
                    "confirmed":True
                }
            )

            speak(
                "Are you sure you want to restart your computer?"
            )

        return True

    elif action == "sleep":

            if data.get("confirmed"):

                speak("Putting computer to sleep")

                ctypes.windll.powrprof.SetSuspendState(
                    False,
                    True,
                    False
                )

            else:

                ask(
                    "sleep",
                    {
                        "action":"sleep",
                        "confirmed":True
                    }
                )

                speak(
                    "Do you want me to put the computer to sleep?"
                )

            return True

    elif action == "lock":

        print("[SYSTEM] Lock")

        try:
            ctypes.windll.user32.LockWorkStation()
            print("[SYSTEM] Locked")
        except Exception as e:
            print(e)

        return True


register("shutdown", system_action)
register("restart", system_action)
register("sleep", system_action)
register("lock", system_action)