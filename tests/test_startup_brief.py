from datetime import datetime

import pytest

from core.startup_brief import build_startup_brief, speak_startup_brief
from skills.assistant import greetings


DAY = datetime(2026, 10, 3, 8, 30)


def brief(**overrides):
    values = {
        "now": DAY,
        "profile": {"name": "Madan.R"},
        "weather_provider": lambda: {
            "location": "Bengaluru",
            "condition": "clear skies",
            "temperature": 30,
        },
        "reminders_provider": lambda: [],
        "tasks_provider": lambda: [],
        "news_enabled": False,
    }
    values.update(overrides)
    return build_startup_brief(**values)


def test_no_meetings_no_reminders_weather_and_news():
    result = brief(
        news_enabled=True,
        news_headlines=[{"title": "Local headline", "category": "world"}],
    )
    assert "Good morning, Madan.R." in result
    assert "Saturday, October 3rd" in result
    assert "clear skies" in result
    assert "Local headline" in result
    assert "meetings" not in result
    assert "It's currently 8:30 AM." in result
    assert "no reminders or scheduled tasks" in result


def test_scheduled_tasks_are_not_called_meetings():
    result = brief(tasks_provider=lambda: [{"id": 1}])
    assert "1 scheduled task today" in result
    assert "meeting" not in result


def test_reminders_are_reported_without_empty_section():
    result = brief(reminders_provider=lambda: [{"text": "Call home"}, {"text": "Pay bill"}])
    assert "2 reminders today" in result


def test_latest_note_is_included_when_provided():
    result = brief(latest_note={"text": "Finish the startup integration"})
    assert "Your latest note says: Finish the startup integration." in result


@pytest.mark.parametrize("provider", [lambda: (_ for _ in ()).throw(RuntimeError("offline")), lambda: None])
def test_weather_failure_is_non_fatal(provider):
    result = brief(weather_provider=provider)
    assert result.startswith("Good morning, Madan.R. Today is")
    assert "weather" not in result.lower()


def test_news_failure_is_non_fatal():
    result = brief(news_enabled=True, news_headlines=None)
    assert "Good morning, Madan.R." in result
    assert "headlines" not in result


def test_schedule_failure_is_non_fatal():
    result = brief(tasks_provider=lambda: (_ for _ in ()).throw(RuntimeError("unavailable")))
    assert "Good morning, Madan.R." in result


@pytest.mark.parametrize(
    ("hour", "opening"),
    [(8, "Good morning"), (14, "Good afternoon"), (19, "Good evening"), (23, "Good evening")],
)
def test_time_contexts(hour, opening):
    assert brief(now=DAY.replace(hour=hour)).startswith(f"{opening}, Madan.R.")


def test_profile_name_is_optional():
    assert brief(profile={}).startswith("Good morning. Today is")


def test_coordinator_failure_uses_original_greeting(monkeypatch):
    spoken = []
    greetings._startup_spoken = False
    monkeypatch.setattr("core.startup_brief.build_startup_brief", lambda **_: (_ for _ in ()).throw(RuntimeError("boom")))
    assert speak_startup_brief(spoken.append, profile={"name": "Madan.R"}, now=DAY)
    assert spoken and "Ready" in spoken[0]
    greetings._startup_spoken = False
