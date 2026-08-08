import os
import shutil
import subprocess

from core.registry import register
from voice.manager import speak
from core.confirmation import ask
from send2trash import send2trash
from core.path_resolver import resolve


def file_action(data):

    action = data.get("action")

    # -----------------------
    # Open File
    # -----------------------

    if action == "open_file":

        path = resolve(
            data.get("path")
        ) or data.get("path")

        if os.path.exists(path):

            os.startfile(path)

            speak("Opening file.")

        else:

            speak("File not found.")

        return True

    # -----------------------
    # Open Folder
    # -----------------------

    elif action == "open_folder":

        path = resolve(
            data.get("path")
        )

        if path is None:
            path = data.get("path")

        if os.path.exists(path):

            if path == "This PC":

                subprocess.Popen(
                    "explorer shell:MyComputerFolder"
                )

            else:

                subprocess.Popen(
                    f'explorer "{path}"'
                )

            speak("Opening folder.")

        else:

            speak("Folder not found.")

        return True

    # -----------------------
    # Create Folder
    # -----------------------

    elif action == "create_folder":

        path = resolve(
            data.get("path")
        ) or data.get("path")

        os.makedirs(
            path,
            exist_ok=True
        )

        speak("Folder created.")

        return True

    # -----------------------
    # Create File
    # -----------------------

    elif action == "create_file":

        path = resolve(
            data.get("path")
        ) or data.get("path")

        open(
            path,
            "a"
        ).close()

        speak("File created.")

        return True

    # -----------------------
    # Copy
    # -----------------------

    elif action == "copy":

        shutil.copy2(

            data["source"],

            data["destination"]

        )

        speak("Copied.")

        return True

    # -----------------------
    # Move
    # -----------------------

    elif action == "move":

        shutil.move(

            data["source"],

            data["destination"]

        )

        speak("Moved.")

        return True

    # -----------------------
    # Rename
    # -----------------------

    elif action == "rename":

        os.rename(

            data["old"],

            data["new"]

        )

        speak("Renamed.")

        return True

    # -----------------------
    # Delete
    # -----------------------

    elif action == "delete":

        if data.get("confirmed"):

            send2trash(data["path"])

            speak("Deleted.")

        else:

            ask(

                "delete",

                {

                    "action":"delete",

                    "path":data["path"],

                    "confirmed":True

                }

            )

            speak(

                "Are you sure you want to delete this file?"

            )

        return True

    return False


register(
    "open_file",
    file_action
)

register(
    "open_folder",
    file_action
)

register(
    "create_file",
    file_action
)

register(
    "create_folder",
    file_action
)

register(
    "copy",
    file_action
)

register(
    "move",
    file_action
)

register(
    "rename",
    file_action
)

register(
    "delete",
    file_action
)