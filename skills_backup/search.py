import os

from core.registry import register
from voice.manager import speak


SEARCH_FOLDERS = [

    os.path.expanduser("~/Desktop"),

    os.path.expanduser("~/Documents"),

    os.path.expanduser("~/Downloads"),

    "D:\\"

]


def search_action(data):

    filename = data.get("filename","").lower()

    results = []

    for root in SEARCH_FOLDERS:

        for path, dirs, files in os.walk(root):

            for file in files:

                if filename in file.lower():

                    full = os.path.join(

                        path,

                        file

                    )

                    results.append(full)

    if results:

        print()

        print("Found Files\n")

        for f in results:

            print(f)

        print()

        speak(

            f"I found {len(results)} matching files."

        )

    else:

        speak(

            "No matching files found."

        )

    return True


register(

    "search_file",

    search_action
)