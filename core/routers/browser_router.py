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
    # Natural Google Search
    # -----------------------------------------------------
    #
    # Examples:
    #
    #   search for artificial intelligence
    #   search artificial intelligence
    #   google search for artificial intelligence
    #   search for Python tutorials on Google
    #
    # IMPORTANT:
    # These must be recognized as WEB searches.
    # File search remains handled by file_router for
    # explicit file/document requests.
    # -----------------------------------------------------

    if command.startswith("search for "):

        query = command[
            len("search for "):
        ].strip()

        if query:

            return [
                {
                    "action": "google_search",
                    "query": query
                }
            ]

    if command.startswith("search ") and not command.endswith(" on youtube"):

        query = command[
            len("search "):
        ].strip()

        if query:

            return [
                {
                    "action": "google_search",
                    "query": query
                }
            ]

    if command.startswith("google search for "):

        query = command[
            len("google search for "):
        ].strip()

        if query:

            return [
                {
                    "action": "google_search",
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

        if query.startswith("for "):
            query = query[4:].strip()

        if not query:
            return None

        return [
            {
                "action": "youtube_search",
                "query": query
            }
        ]
        
    # -----------------------------------------------------
    # Search <query> on YouTube
    # -----------------------------------------------------

    if command.startswith("search ") and command.endswith(" on youtube"):

        query = command[
            len("search "):-len(" on youtube")
        ].strip()

        if query:
            return [
                {
                    "action": "youtube_search",
                    "query": query
                }
            ]
        
    # -----------------------------------------------------
    # YouTube Controls
    # -----------------------------------------------------

    # -----------------------------------------------------
    # YouTube Play First Video
    # -----------------------------------------------------

    if command.startswith("play first youtube video for "):

        query = command.replace(
            "play first youtube video for ",
            "",
            1
        ).strip()

        if query:
            return [
                {
                    "action": "youtube_play_first",
                    "query": query
                }
            ]


    if command.startswith("play youtube video for "):

        query = command.replace(
            "play youtube video for ",
            "",
            1
        ).strip()

        if query:
            return [
                {
                    "action": "youtube_play_first",
                    "query": query
                }
            ]


    if command.startswith("play first video for "):

        query = command.replace(
            "play first video for ",
            "",
            1
        ).strip()

        if query:
            return [
                {
                    "action": "youtube_play_first",
                    "query": query
                }
            ]


    # -----------------------------------------------------
    # YouTube Play First Video - Current Search
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


    # -----------------------------------------------------
    # YouTube Pause
    # -----------------------------------------------------

    if command in [
        "pause youtube",
        "pause youtube video",
        "pause video",
        "pause the video",
        "pause",
    ]:

        return [
            {
                "action": "youtube_pause"
            }
        ]


    # -----------------------------------------------------
    # YouTube Resume
    # -----------------------------------------------------

    if command in [
        "resume youtube",
        "resume youtube video",
        "resume the youtube video",
        "resume video",
        "resume the video",
        "continue youtube",
        "continue the youtube video",
        "continue video",
        "continue the video",
        "continue playing",
    ]:

        return [
            {
                "action": "youtube_resume"
            }
        ]


    # -----------------------------------------------------
    # YouTube Next
    # -----------------------------------------------------

    if command in [
        "next youtube",
        "next youtube video",
        "next the youtube video",
        "next video",
        "next the video",
        "play next video",
        "play the next video",
        "play next youtube video",
        "play the next youtube video",
    ]:
        return [
            {
                "action": "youtube_next"
            }
        ]


    # -----------------------------------------------------
    # YouTube Previous
    # -----------------------------------------------------

    if command in [
        "previous youtube",
        "previous youtube video",
        "previous the youtube video",
        "previous video",
        "previous the video",
        "play previous video",
        "play the previous video",
        "play previous youtube video",
        "play the previous youtube video",
    ]:
        return [
            {
                "action": "youtube_previous"
            }
        ]
        
    # -----------------------------------------------------
    # Browser Navigation Controls
    # -----------------------------------------------------

    # New Tab
    if command in [
        "new tab",
        "open new tab",
        "open a new tab",
        "create new tab",
    ]:
        return [
            {
                "action": "new_tab"
            }
        ]

    # Back
    if command in [
        "back",
        "go back",
        "go backward",
        "go to previous page",
        "previous page",
    ]:
        return [
            {
                "action": "back"
            }
        ]

    # Forward
    if command in [
        "forward",
        "go forward",
        "go forwards",
        "go to next page",
        "next page",
    ]:
        return [
            {
                "action": "forward"
            }
        ]

    # Refresh
    if command in [
        "refresh",
        "refresh page",
        "refresh the page",
        "reload",
        "reload page",
        "reload the page",
    ]:
        return [
            {
                "action": "refresh"
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