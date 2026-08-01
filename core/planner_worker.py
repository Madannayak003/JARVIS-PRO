from ai.planner import create_plan
from core.executor import execute_ai_plan
from core.busy_manager import start_task, finish_task


def planner_worker(command, stop_event):

    print("[PLANNER WORKER]")

    start_task("planner")

    try:

        plan = create_plan(command, stop_event)

    finally:
        # Planning finished here
        finish_task()

    if stop_event.is_set():
        return

    if not plan:
        return

    execute_ai_plan(plan, stop_event)