from datetime import datetime

from core.routers.schedule_router import schedule_route


def test_relative_natural_schedule_routes_to_create_schedule():
    before = datetime.now()
    plan = schedule_route("Schedule a task to open Chrome at 10 minutes from now")
    after = datetime.now()

    assert plan[0]["action"] == "create_schedule"
    assert plan[0]["command"] == "open Chrome"
    assert plan[0]["recurrence"] == "none"

    run_at = datetime.fromisoformat(plan[0]["run_at"])
    assert before.timestamp() + 9 * 60 <= run_at.timestamp() <= after.timestamp() + 11 * 60
