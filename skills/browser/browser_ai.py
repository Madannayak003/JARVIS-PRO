from core.registry import register
from voice.manager import speak
from skills.browser.navigation import navigation
from core.action_memory import set_memory
from core.action_memory import dump
from skills.browser.browser_controller import browser

from core.live_execution import is_live_execution

from core.browser_context import browser_context

import os

SITES = {

    "chrome": "https://www.google.com",

    "google": "https://www.google.com",

    "youtube": "https://www.youtube.com",

    "gmail": "https://mail.google.com",

    "github": "https://github.com",

    "spotify": "https://open.spotify.com",

    "chatgpt": "https://chat.openai.com",

}


WINDOWS_APPS = {

    "notepad": "notepad",

    "calculator": "calc",

    "calc": "calc",

    "paint": "mspaint",

    "cmd": "cmd",

    "command prompt": "cmd",

    "powershell": "powershell",

    "explorer": "explorer",
    
    "file explorer": "explorer",

    "task manager": "taskmgr",

    "registry editor": "regedit",

    "device manager": "devmgmt.msc",

    "control panel": "control",

    "settings": "ms-settings:",

}


def ai_open(data):

    app = data.get("app", "").lower()

    # ---------- Websites ----------

    if app in SITES:

        if not is_live_execution():
            speak(f"Opening {app}")

        navigation.open(SITES[app])
        
        browser_context.set_page(
            url=SITES[app],
            site=app,
        )

        # Action Memory
        set_memory("app", app)
        set_memory("site", app)
        set_memory("action", "open")
        
        print("[MEMORY]", dump())

        return True

    # ---------- Windows Apps ----------

    if app in WINDOWS_APPS:

        speak(f"Opening {app}")

        os.startfile(WINDOWS_APPS[app])

        # Action Memory
        set_memory("app", app)
        set_memory("action", "open")
        
        print("[MEMORY]", dump())

        return True


def ai_google(data):

    query = data.get("query", "").strip()

    if not query:
        return False

    if not is_live_execution():
        speak(f"Searching Google for {query}")

    result = browser.search_google(query)

    browser_context.set_page(
        site="google",
    )

    if not result:
        print("[Google] Search failed")
        return False

    # Action Memory
    set_memory("site", "google")
    set_memory("search", query)
    set_memory("action", "google_search")
    set_memory("search_platform", "google")

    print("[MEMORY]", dump())

    return True


def ai_youtube(data):

    query = data.get("query", "")

    if not is_live_execution():
        speak(f"Searching YouTube for {query}")

    navigation.youtube(query)
    
    browser_context.set_search(
        query=query,
        platform="youtube",
        results=[],
    )

    browser_context.set_page(
        site="youtube",
    )
    
    # Action Memory 
    set_memory("site", "youtube")
    set_memory("search", query)
    set_memory("action", "youtube_search")
    set_memory("search_platform", "youtube")
    
    print("[MEMORY]", dump())

    return True


register("open", ai_open)

register("google_search", ai_google)