from click import command

from ai.intent import detect

from core.task_manager import task_manager
from core.workers import chat_worker
from core.planner_worker import planner_worker
from core.action_memory import get_memory
from core.executor import execute_ai_plan
from core.action_memory import get_memory
from core.action_memory import set_memory

from ai.memory_pipeline import learn
from ai.memory_view import show_all
from ai.memory_intent import handle as memory_forget
from ai.memory_profile import profile_summary

from core.context import (
    get_value,
    set_value
)

from ai.memory_stats import (
    total,
    by_category
)

from brain.brain_router import BrainRouter

brain_router = BrainRouter()

def dispatch(command):
    
    command = command.lower().strip()
    
    # ---------------------------------
    # Clarification Context
    # ---------------------------------

    clarify = get_memory("clarify_context")

    if clarify:

        subject = clarify.get("subject")

        ctype = clarify.get("type")

        if ctype == "generic_action":

            cmd = command.lower()

            if cmd in [
                "google",
                "search google",
                "search on google",
                "on google"
            ]:

                set_memory("clarify_context", None)

                execute_ai_plan(
                    [{
                        "action": "google_search",
                        "query": subject
                    }],
                    task_manager.event("planner")
                )

                return

            elif cmd in [
                "youtube",
                "search youtube",
                "search on youtube",
                "on youtube"
            ]:

                set_memory("clarify_context", None)

                execute_ai_plan(
                    [{
                        "action": "youtube_search",
                        "query": subject
                    }],
                    task_manager.event("planner")
                )

                return

            elif cmd in [
                "github",
                "search github"
            ]:

                set_memory("clarify_context", None)

                execute_ai_plan(
                    [{
                        "action": "github_search",
                        "query": subject
                    }],
                    task_manager.event("planner")
                )

                return

            elif cmd in [
                "chatgpt",
                "search chatgpt"
            ]:

                set_memory("clarify_context", None)

                execute_ai_plan(
                    [{
                        "action": "chatgpt_search",
                        "query": subject
                    }],
                    task_manager.event("planner")
                )

                return

    # -----------------------------
    # Fast search using Action Memory
    # -----------------------------
    
    memory_result = learn(command)

    # ---------------------------------
    # Memory Saved
    # ---------------------------------

    if memory_result.get("saved"):

        print(
            f"[MEMORY] Saved -> "
            f"{memory_result['key']} = "
            f"{memory_result['value']}"
        )

        if memory_result.get("updated"):

            from voice.manager import speak

            speak(
                f"I've updated your {memory_result['key']}."
            )

        else:

            from voice.manager import speak

            speak(
                f"I'll remember that."
            )

        return

    # ---------------------------------
    # Already Known
    # ---------------------------------

    if memory_result.get("already_known"):

        from voice.manager import speak

        print("[MEMORY] Already known.")

        speak("I already knew that.")

        return
    
    
    # ---------------------------------
    # Show Stored Memories
    # ---------------------------------

    MEMORY_VIEW_COMMANDS = (

        "show my memories",

        "list my memories",

        "show all memories",

        "what do you know about me",

        "show everything you know"

    )

    if command in MEMORY_VIEW_COMMANDS:

        from voice.manager import speak

        result = show_all()

        print("\n[MEMORY VIEW]\n")

        print(result)

        speak(result)

        return
    
    # ---------------------------------
    # User Profile
    # ---------------------------------

    PROFILE_COMMANDS = (

        "show my profile",

        "my profile",

        "user profile",

        "profile",

        "summarize me",

        "summarize my profile"

    )

    if command in PROFILE_COMMANDS:

        from voice.manager import speak

        profile = profile_summary()

        print("\n[USER PROFILE]\n")

        print(profile)

        speak(profile)

        return
    
    # ---------------------------------
    # Memory Statistics
    # ---------------------------------

    MEMORY_STATS_COMMANDS = (

        "memory statistics",

        "memory stats",

        "show memory statistics",

        "how many memories do you have",

        "how many things do you remember"

    )

    if command in MEMORY_STATS_COMMANDS:

        from voice.manager import speak

        count = total()

        categories = by_category()

        text = f"I currently remember {count} thing"

        if count != 1:

            text += "s"

        text += ".\n"

        for category, value in categories.items():

            text += f"\n{category.title()} : {value}"

        print("\n[MEMORY STATS]\n")

        print(text)

        speak(text)

        return
    
    # ---------------------------------
    # Forget Memory
    # ---------------------------------

    forget_result = memory_forget(command)

    if forget_result:

        from voice.manager import speak

        print("\n[MEMORY FORGET]\n")

        print(forget_result)

        if forget_result["type"] == "key":

            message = (
                f"I forgot your "
                f"{forget_result['key']}."
            )

        elif forget_result["type"] == "category":

            deleted = len(

                forget_result["deleted"]

            )

            message = (

                f"I forgot "

                f"{deleted} "

                f"memories from "

                f"{forget_result['category']}."

            )

        else:

            deleted = len(

                forget_result["deleted"]

            )

            message = (

                f"I forgot "

                f"{deleted} memories."

            )

        speak(message)

        return


    pending = get_memory("pending_subject")

    if pending and command.startswith("search on"):

        platform = command.replace("search on", "").strip()

        print("[PENDING SUBJECT]", pending)

        if platform == "youtube":

            execute_ai_plan(
                [{
                    "action":"youtube_search",
                    "query": pending
                }],
                task_manager.event("planner")
            )

            set_memory("pending_subject", None)

            return

        elif platform == "google":

            execute_ai_plan(
                [{
                    "action":"google_search",
                    "query": pending
                }],
                task_manager.event("planner")
            )

            set_memory("pending_subject", None)

            return

        elif platform == "github":

            execute_ai_plan(
                [{
                    "action":"github_search",
                    "query": pending
                }],
                task_manager.event("planner")
            )

            set_memory("pending_subject", None)

            return

    if (
        command.startswith("search ")
        and "youtube" not in command
        and "google" not in command
        and "github" not in command
        and "chatgpt" not in command
    ):

        current_site = get_memory("site")

        query = command.replace("search", "", 1).strip()

        if current_site == "youtube":

            print("[ACTION MEMORY] YouTube Search")

            task_manager.start(
                "executor",
                execute_ai_plan,
                [{
                    "action": "youtube_search",
                    "query": query
                }]
            )

            return

        if current_site == "google":

            print("[ACTION MEMORY] Google Search")

            task_manager.start(
                "executor",
                execute_ai_plan,
                [{
                    "action": "google_search",
                    "query": query
                }]
            )

            return

    # -------------------------------------------------
    # Brain Router
    # -------------------------------------------------

    brain_result = brain_router.route(command)

    if brain_result.handled:

        print("[BRAIN ROUTER] Developer module handled request.")

        return

    # -------------------------------------------------
    # Existing Chat / Planner
    # -------------------------------------------------

    mode = detect(command)

    # Continue conversation

    if get_value("chat_mode"):
        mode = "chat"

    if mode == "chat":

        task_manager.start(

            "chat",

            chat_worker,

            command

        )

    else:

        task_manager.start(

            "planner",

            planner_worker,

            command

        )