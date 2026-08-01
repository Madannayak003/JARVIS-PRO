import time
from voice.manager import speak
from config.settings import WAKE_WORDS

from core.confirmation import waiting
from core.confirmation import get

from core.confirmation import clear
from core.registry import execute

from core.listener import start_listener
from core.listener import get_command

from core.runtime import handle_priority

from core.dispatcher import dispatch

from core.action_memory import set_memory

from core.interrupt import interrupt

from skills.greetings import startup_greeting

from core.whatsapp_memory import (
    get_contact,
    clear_contact,
    get_pending_message,
    clear_pending_message,
)

from core.context import (
    add_message,
    get_value,
    set_value
)

from core.power import (
    sleep,
    wake,
    shutdown
)

from core.busy_manager import (
    is_busy,
    ask_switch
)

def run():

    speak(startup_greeting())

    start_listener()

    while True:

        query = get_command()

        if not query:

            time.sleep(0.05)

            continue
        
        if handle_priority(query):
            
            time.sleep(0.05)
            
            continue
        
        query = query.strip()
        
        # ---------------------------------
        # Waiting for WhatsApp message?
        # ---------------------------------
        
        pending = get_pending_message()

        if pending is not None:

            clear_pending_message()

            dispatch(f"message {query}")

            continue
            
        contact = get_contact()
        
        print("[WA] Pending contact:", contact)

        if contact:

            clear_contact()

            dispatch(f"message {contact} {query}")

            continue        
        
        # ----------------------------
        # Busy Manager
        # ----------------------------

        if is_busy() and not waiting():

            ask_switch(query)

            speak(
                f"I'm still working on your previous request.\n"
                f'Should I stop it and continue with "{query}"?'
            )

            continue
        
        state = get_value("state")
        
        if state == "sleep":

            if query.startswith("jarvis"):

                wake()

            continue
        
        if query.lower() in [

            "go offline",

            "jarvis go offline",

            "sleep",

            "jarvis sleep",
            
            "jarvis sleep mode"

        ]:

            sleep()

            continue
        
        if query.lower() in [

            "shutdown",

            "terminate",

            "power off",

            "jarvis shutdown",

            "jarvis terminate"

        ]:

            shutdown()
            continue
        
        if waiting():

            q = query.lower()
            
            pending = get()
            
            # ----------------------------
            # Busy Manager Confirmation
            # ----------------------------

            if pending and pending.get("action") == "switch_task":

                if q in [
                    "yes",
                    "sure",
                    "okay",
                    "ok",
                    "go ahead",
                    "continue",
                    "yes please",
                    "yes continue",
                    "yes do it",
                    "yes switch"
                ]:
                    new_command = pending["new_command"]

                    interrupt()

                    clear()

                    dispatch(new_command)

                    continue

                elif q in [
                    "no",
                    "no thanks",
                    "never mind",
                    "stay",
                    "keep going"
                ]:
                    speak("Okay. I'll ignore the new request.")
                    clear()
                    continue

            # ----------------------------
            # Search platform clarification
            # ----------------------------

            if pending and "context" in pending:

                ctx = pending["context"]

                if "pending_search" in ctx:

                    platforms = {

                                "google": "google_search",

                                "youtube": "youtube_search",

                                "github": "github_search",

                                "chatgpt": "chatgpt_search"

                            }
    
                    for platform, action in platforms.items():

                                if platform in q:

                                    from core.action_memory import set_memory

                                    set_memory("search_platform", platform)

                                    execute(
                                        action,
                                        {
                                            "query": ctx["pending_search"]
                                        }
                                    )

                                    clear()

                                    break

                    if not waiting():

                     continue
                            
                    pending = get()
                            
            if q in [
                "yes",
                "yes sir",
                "confirm",
                "do it",
                "okay",
                "ok"
            ]:

                pending = get()

                execute(
                    pending["action"],
                    pending["data"]
                )

                clear()

                continue

            elif q in [
                "no",
                "cancel",
                "stop",
                "don't",
                "dont"
            ]:

                speak("Cancelled.")

                set_value("chat_mode", False)

                clear()

                continue
                    
        add_message("user", query)

        # Wake words
        if any(query.startswith(word) for word in WAKE_WORDS):

            remaining = query

            for word in WAKE_WORDS:

                if remaining.startswith(word):

                    remaining = remaining.replace(word, "", 1).strip()

                    break

            if remaining == "":

                if state == "sleep":
                    wake()
                else:
                    speak("Yes Sir.")

                continue

            speak("Yes Sir.")

            dispatch(remaining)
            
            continue
        
        dispatch(query)