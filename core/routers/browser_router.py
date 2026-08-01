WINDOWS_APPS = [

    "notepad",
    "calculator",
    "calc",
    "paint",
    "cmd",
    "command prompt",
    "powershell",
    "explorer",
    "file explorer",
    "settings",
    "control panel",
    "task manager"

]


def browser_route(command):

    command = command.lower().strip()

    # ---------- Open Google Search ----------

    if command.startswith("open google search"):

        query = command.replace(
            "open google search",
            ""
        ).strip()

        return [

            {
                "action": "open",
                "app": "google"
            },

            {
                "action": "google_search",
                "query": query
            }

        ]

    # ---------- Open YouTube Search ----------

    if command.startswith("open youtube search"):

        query = command.replace(
            "open youtube search",
            ""
        ).strip()

        return [

            {
                "action": "open",
                "app": "youtube"
            },

            {
                "action": "youtube_search",
                "query": query
            }

        ]

    # ---------- Google Search ----------

    if command.startswith("search google"):

        query = command.replace(
            "search google",
            ""
        ).strip()

        return [

            {
                "action": "google_search",
                "query": query
            }

        ]

    # ---------- YouTube Search ----------

    if command.startswith("search youtube"):

        query = command.replace(
            "search youtube",
            ""
        ).strip()

        return [

            {
                "action": "youtube_search",
                "query": query
            }

        ]

    # ---------- Windows Apps ----------

    if command.startswith("open "):

        app = command.replace("open", "", 1).strip()

        if app in WINDOWS_APPS:

            return [

                {
                    "action": "open",
                    "app": app
                }

            ]

    # ---------- Websites ----------

    browser_commands = {

        "open google": [
            {
                "action": "open",
                "app": "google"
            }
        ],

        "google": [
            {
                "action": "open",
                "app": "google"
            }
        ],

        "open youtube": [
            {
                "action": "open",
                "app": "youtube"
            }
        ],

        "youtube": [
            {
                "action": "open",
                "app": "youtube"
            }
        ],

        "open chrome": [
            {
                "action": "open",
                "app": "chrome"
            }
        ]

    }

    return browser_commands.get(command)