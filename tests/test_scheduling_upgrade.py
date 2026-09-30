import json
from datetime import datetime, timedelta


def test_schedule_router_supports_one_time_and_daily_commands():
    from core.routers.schedule_router import schedule_route

    one_time = schedule_route("schedule a task tomorrow at 9 AM to open VS Code")
    daily = schedule_route("schedule a task every day at 8 AM to open VS Code")

    assert one_time[0]["action"] == "create_schedule"
    assert one_time[0]["recurrence"] == "none"
    assert daily[0]["recurrence"] == "daily"


def test_scheduler_persists_and_cancels(tmp_path, monkeypatch):
    import skills.automation.scheduling as scheduling

    monkeypatch.setattr(scheduling, "DATA_FILE", tmp_path / "schedules.json")
    monkeypatch.setattr(scheduling, "speak", lambda *_args: None)

    item = scheduling.create_schedule({
        "command": "open VS Code",
        "run_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    })

    assert item["id"] == 1
    assert scheduling.list_schedules()[0]["command"] == "open VS Code"
    assert scheduling.cancel_schedule({"id": 1}) is True
    assert scheduling.list_schedules()[0]["enabled"] is False


def test_scheduler_uses_injected_trusted_executor(tmp_path, monkeypatch):
    import skills.automation.scheduling as scheduling

    monkeypatch.setattr(scheduling, "DATA_FILE", tmp_path / "schedules.json")
    monkeypatch.setattr(scheduling, "speak", lambda *_args: None)
    calls = []
    scheduling.set_executor(calls.append)
    scheduling.create_schedule({
        "command": "open VS Code",
        "run_at": (datetime.now() - timedelta(seconds=1)).isoformat(),
    })

    scheduling._run_due()

    assert calls == ["open VS Code"]
    assert scheduling.list_schedules()[0]["enabled"] is False
    scheduling.set_executor(None)
