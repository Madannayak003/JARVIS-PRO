from core.registry import execute
from core.context import set_value
from core.action_memory import set_memory


def execute_ai_plan(
    plan,
    stop_event,
    original_request=None,
):
    
    for raw_step in plan:

        # Keep the planner's original request available to a clarification
        # action without mutating the plan object shared by callers.
        step = dict(raw_step)

        if (
            step.get("action") == "clarify"
            and original_request
            and not step.get("original_request")
        ):
            step["original_request"] = original_request

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
