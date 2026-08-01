import psutil

from core.registry import register
from voice.manager import speak


def process_action(data):

    action = data.get("action")

    if action == "running_apps":

        print("\nRunning Processes\n")

        for p in psutil.process_iter(["name"]):

            try:

                print(p.info["name"])

            except:

                pass

        speak("Running processes are listed in the terminal.")

        return True

    elif action == "close_process":

        target = data.get("process","").lower()

        for p in psutil.process_iter(["pid","name"]):

            try:

                name = p.info["name"].lower()

                if target in name:

                    psutil.Process(
                        p.info["pid"]
                    ).terminate()

                    speak(f"Closed {target}")

                    return True

            except:

                pass

        speak("Process not found.")

        return True

    return False


register("running_apps", process_action)
register("close_process", process_action)