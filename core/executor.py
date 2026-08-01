from core.registry import execute
from core.context import set_value
from core.action_memory import set_memory


def execute_ai_plan(plan, stop_event):
    
    for step in plan:

        if stop_event and stop_event.is_set():
            print("[EXECUTOR] Cancelled")
            return

        action = step["action"]

        print(f"\nExecuting {action}")

        # Existing context
        set_value("last_action", action)
        set_value("last_query", step)

        # -------- Action Memory --------

        set_memory("action", action)

        if "app" in step:
            set_memory("app", step["app"])

        if "query" in step:
            set_memory("search", step["query"])

        execute(action, step)