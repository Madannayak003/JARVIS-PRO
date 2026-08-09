"""
JARVIS PRO
Browser Router

Routes normal browser websites, searches,
and Windows applications.

Personal/custom web destinations are handled
by web_router.py and must not be duplicated here.
"""

# =========================================================
# Windows Applications
# =========================================================

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
    "task manager",
    "registry editor",
    "device manager",
    "control panel",
    "settings",
]


# =========================================================
# Browser Websites
# =========================================================

BROWSER_SITES = [
    "google",
    "youtube",
    "chrome",
    "gmail",
    "github",
    "spotify",
    "chatgpt",
]


# =========================================================
# Browser Router
# =========================================================

def browser_route(command):

    if not command:
        return None

    command = str(command).strip().lower()

    if not command:
        return None

    # -----------------------------------------------------
    # Open Google Search
    # -----------------------------------------------------

    if command.startswith("open google search"):

        query = command.replace(
            "open google search",
            "",
            1
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

    # -----------------------------------------------------
    # Open YouTube Search
    # -----------------------------------------------------

    if command.startswith("open youtube search"):

        query = command.replace(
            "open youtube search",
            "",
            1
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

    # -----------------------------------------------------
    # Google Search
    # -----------------------------------------------------

    if command.startswith("search google"):

        query = command.replace(
            "search google",
            "",
            1
        ).strip()

        return [
            {
                "action": "google_search",
                "query": query
            }
        ]

    # -----------------------------------------------------
    # YouTube Search
    # -----------------------------------------------------

    if command.startswith("search youtube"):

        query = command.replace(
            "search youtube",
            "",
            1
        ).strip()

        return [
            {
                "action": "youtube_search",
                "query": query
            }
        ]
        
    # -----------------------------------------------------
    # YouTube Controls
    # -----------------------------------------------------

    if command in [
        "play youtube",
        "play youtube video",
        "play first youtube video",
        "play first video",
    ]:

        return [
            {
                "action": "youtube_play_first"
            }
        ]


    if command in [
        "pause youtube",
        "pause youtube video",
        "pause video",
    ]:

        return [
            {
                "action": "youtube_pause"
            }
        ]


    if command in [
        "resume youtube",
        "resume youtube video",
        "resume video",
        "continue youtube",
    ]:

        return [
            {
                "action": "youtube_resume"
            }
        ]


    if command in [
        "next youtube",
        "next youtube video",
        "next video",
    ]:

        return [
            {
                "action": "youtube_next"
            }
        ]


    if command in [
        "previous youtube",
        "previous youtube video",
        "previous video",
    ]:

        return [
            {
                "action": "youtube_previous"
            }
        ]    

    # -----------------------------------------------------
    # Windows Applications
    # -----------------------------------------------------

    if command.startswith("open "):

        app = command.replace(
            "open ",
            "",
            1
        ).strip()

        if app in WINDOWS_APPS:

            return [
                {
                    "action": "open",
                    "app": app
                }
            ]

    # -----------------------------------------------------
    # Browser Websites
    # -----------------------------------------------------

    if command.startswith("open "):

        site = command.replace(
            "open ",
            "",
            1
        ).strip()

        if site in BROWSER_SITES:

            return [
                {
                    "action": "open",
                    "app": site
                }
            ]

    # -----------------------------------------------------
    # Direct website names
    # -----------------------------------------------------

    if command in BROWSER_SITES:

        return [
            {
                "action": "open",
                "app": command
            }
        ]

    return None