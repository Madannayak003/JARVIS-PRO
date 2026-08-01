import json

from ai.ollama import ask_ollama
from ai.planner_prompt import SYSTEM_PROMPT
from core.context import get_history
from core.context import get_value

from core.fast_router import fast_route

from core.action_memory import get_memory

from core.action_memory import set_memory

from core.app_resolver import resolve_app

def create_plan(command, stop_event):

    command = command.strip().lower()
    
    if stop_event.is_set():
        return None
    
    print("[PLANNER] Command:", command)
    
    plan = fast_route(command)
    
    print("[PLANNER] Fast Route:", plan)

    if plan:
        return plan
    
    # -------------------------------
    # Smart Search Platform Memory V2
    # -------------------------------

    if command.startswith("search "):

        query = command.replace("search", "", 1).strip()

        # ---------------- Explicit platform ----------------

        PLATFORM_MAP = {
            "youtube": "youtube_search",
            "google": "google_search",
            "github": "github_search",
            "chatgpt": "chatgpt_search"
        }

        for platform, action in PLATFORM_MAP.items():

            if f" on {platform}" in query or f" in {platform}" in query:

                clean_query = (
                    query.replace(f" on {platform}", "")
                        .replace(f" in {platform}", "")
                        .strip()
                )

                return [{
                    "action": action,
                    "query": clean_query
                }]

        # ---------------- Use remembered platform ----------------

        platform = get_memory("search_platform")

        if platform:

            print(f"[SMART SEARCH] Using {platform}")

            if platform == "youtube":

                return [{
                    "action": "youtube_search",
                    "query": query
                }]

            elif platform == "google":

                return [{
                    "action": "google_search",
                    "query": query
                }]

            elif platform == "github":

                return [{
                    "action": "github_search",
                    "query": query
                }]

            elif platform == "chatgpt":

                return [{
                    "action": "chatgpt_search",
                    "query": query
                }]

        # ---------------- Ask first time ----------------

        return [{
            "action": "clarify",
            "question": "Where would you like me to search? Google, YouTube, GitHub or ChatGPT?",
            "context": {
                "pending_search": query
            }
        }]
    
    # ---------- Simple browser shortcuts -----------

    if command.startswith("open google search"):
        return fast_route(command)

    if command.startswith("open youtube search"):
        return fast_route(command)

    if command.startswith("search google"):
        return fast_route(command)

    if command.startswith("search youtube"):
        return fast_route(command)
    
    # ---------- Fast System Commands ----------

    if "shutdown" in command:
        return [{"action": "shutdown"}]

    if "restart" in command:
        return [{"action": "restart"}]

    if "sleep" in command:
        return [{"action": "sleep"}]

    if "lock" in command:
        return [{"action": "lock"}]

    
    # -------------------------------
    # Smart App Resolver
    # -------------------------------

    app = resolve_app(command)

    if app:

        print(f"[SMART APP] {app}")

        return [{
            "action": "open",
            "app": app
        }]
    
    # -------- Incomplete Commands --------

    if command == "open":
        return [{
            "action": "clarify",
            "question": "What would you like me to open?"
        }]

    if command == "play":
        return [{
            "action": "clarify",
            "question": "What would you like me to play?"
        }]

    if command == "search":
        return [{
            "action": "clarify",
            "question": "What would you like me to search for?"
        }]

    # Continue with Ollama
    if stop_event.is_set():
        return None
    
    history = get_history()

    current_app = get_value("current_app")

    history_text = ""

    for item in history[-10:]:

        history_text += f"{item['role']}: {item['text']}\n"

    prompt = f"""
    Current App:
    {current_app}

    Conversation:
    {history_text}

    User Command:
    {command}
    """

    answer = ask_ollama(
        SYSTEM_PROMPT,
        prompt
    )
    
    if stop_event.is_set():
        return None

    answer = answer.strip()

    if answer.startswith("```"):
        answer = (
            answer.replace("```json", "")
                .replace("```", "")
                .strip()
        )

    print("\n========== AI PLAN ==========")
    print(answer)
    print("=============================\n")

    try:

        return json.loads(answer)

    except Exception as e:

        print("Planner Error:", e)

        return [
            {
                "action": "clarify",
                "question": f"What would you like to do with '{command}'?",
                "context": {
                    "subject": command,
                    "type": "generic_action"
                }
            }
        ]