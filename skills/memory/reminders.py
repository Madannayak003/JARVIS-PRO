"""
JARVIS PRO
Reminder Skill

Handles:
- Create reminders
- List reminders
- Cancel reminders
- Automatic background reminder checking
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path

from core.registry import register
from voice.manager import speak
from datetime import datetime, timedelta

# =========================================================
# Storage
# =========================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

REMINDERS_FILE = DATA_DIR / "reminders.json"


# =========================================================
# Scheduler Configuration
# =========================================================

CHECK_INTERVAL = 5

_scheduler_started = False
_scheduler_lock = threading.Lock()


# =========================================================
# Storage
# =========================================================

def _load_reminders():

    if not REMINDERS_FILE.exists():
        return []

    try:

        with open(
            REMINDERS_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        if isinstance(data, list):
            return data

    except Exception as e:

        print(
            f"[REMINDERS ERROR] Load failed: {e}"
        )

    return []


def _save_reminders(reminders):

    try:

        with open(
            REMINDERS_FILE,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                reminders,
                f,
                indent=4,
                ensure_ascii=False,
            )

        return True

    except Exception as e:

        print(
            f"[REMINDERS ERROR] Save failed: {e}"
        )

        return False


# =========================================================
# Create Reminder
# =========================================================

def create_reminder(data=None):

    data = data or {}

    text = str(
        data.get("text", "")
    ).strip()

    remind_at = str(
        data.get("remind_at", "")
    ).strip()

    if not text:

        speak(
            "What should I remind you about?"
        )

        return False

    if not remind_at:

        speak(
            "When should I remind you?"
        )

        return False

    reminders = _load_reminders()

    next_id = 1

    if reminders:

        next_id = max(
            int(r.get("id", 0))
            for r in reminders
        ) + 1

    reminder = {
        "id": next_id,
        "text": text,
        "remind_at": remind_at,
        "created_at": datetime.now().isoformat(),
        "completed": False,
    }

    reminders.append(reminder)

    if not _save_reminders(reminders):

        speak(
            "I couldn't save that reminder."
        )

        return False

    print(
        "[REMINDER] Created:",
        reminder,
    )

    speak(
        f"I'll remind you to {text} at {remind_at}."
    )

    return True


# =========================================================
# List Reminders
# =========================================================

def list_reminders(data=None):

    reminders = _load_reminders()

    active = [
        r
        for r in reminders
        if not r.get("completed", False)
    ]

    if not active:

        speak(
            "You don't have any active reminders."
        )

        return True

    print("\n[REMINDERS]")

    for reminder in active:

        print(
            f"{reminder['id']}. "
            f"{reminder['text']} "
            f"-> {reminder['remind_at']}"
        )

    speak(
        f"You have {len(active)} active reminders."
    )

    return True


# =========================================================
# Cancel Reminder
# =========================================================

def cancel_reminder(data=None):

    data = data or {}

    reminder_id = data.get("id")

    if reminder_id is None:

        speak(
            "Which reminder should I cancel?"
        )

        return False

    reminders = _load_reminders()

    found = False

    for reminder in reminders:

        if str(
            reminder.get("id")
        ) == str(reminder_id):

            reminder["completed"] = True
            found = True

            break

    if not found:

        speak(
            "I couldn't find that reminder."
        )

        return False

    if not _save_reminders(reminders):

        speak(
            "I couldn't cancel that reminder."
        )

        return False

    speak(
        "The reminder has been cancelled."
    )

    return True


# =========================================================
# Reminder Scheduler
# =========================================================

def _reminder_scheduler():

    print(
        "[REMINDERS] Automatic scheduler started"
    )

    while True:

        try:

            reminders = _load_reminders()

            now = datetime.now()

            changed = False

            for reminder in reminders:

                if reminder.get(
                    "completed",
                    False,
                ):

                    continue

                remind_at = str(
                    reminder.get(
                        "remind_at",
                        "",
                    )
                ).strip()

                if not remind_at:
                    continue

                target = _parse_reminder_time(
                    remind_at
                )

                if target is None:

                    print(
                        "[REMINDERS] Invalid time:",
                        remind_at,
                    )

                    continue

                if now >= target:

                    text = reminder.get(
                        "text",
                        "your reminder",
                    )

                    print(
                        "[REMINDERS] Triggered:",
                        text,
                    )

                    speak(
                        f"Sir, here's your reminder. "
                        f"You asked me to {text}."
                    )

                    reminder["completed"] = True

                    reminder["triggered_at"] = (
                        now.isoformat()
                    )

                    changed = True

            if changed:

                _save_reminders(
                    reminders
                )

        except Exception as e:

            print(
                f"[REMINDERS SCHEDULER ERROR] {e}"
            )

        time.sleep(
            CHECK_INTERVAL
        )


# =========================================================
# Start Scheduler
# =========================================================

def start_reminder_scheduler():

    global _scheduler_started

    with _scheduler_lock:

        if _scheduler_started:
            return

        _scheduler_started = True

        thread = threading.Thread(
            target=_reminder_scheduler,
            daemon=True,
            name="ReminderScheduler",
        )

        thread.start()
        
# =========================================================
# Parse Reminder Time
# =========================================================

def _parse_reminder_time(value):
    """
    Convert common reminder time formats into datetime.

    Supported:
        2026-08-09T10:30:00
        10:30 PM
        10:30 AM
        22:30
    """

    value = str(value).strip()

    if not value:
        return None

    # -----------------------------------------
    # ISO datetime
    # -----------------------------------------

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    # -----------------------------------------
    # 12-hour time
    # -----------------------------------------

    for fmt in (
        "%I:%M %p",
        "%I %p",
    ):

        try:

            parsed = datetime.strptime(
                value.upper(),
                fmt,
            )

            now = datetime.now()

            result = now.replace(
                hour=parsed.hour,
                minute=parsed.minute,
                second=0,
                microsecond=0,
            )

            # If today's time already passed,
            # interpret it as tomorrow.
            if result <= now:

                result += timedelta(
                    days=1
                )

            return result

        except ValueError:
            pass

    # -----------------------------------------
    # 24-hour time
    # -----------------------------------------

    try:

        parsed = datetime.strptime(
            value,
            "%H:%M",
        )

        now = datetime.now()

        result = now.replace(
            hour=parsed.hour,
            minute=parsed.minute,
            second=0,
            microsecond=0,
        )

        if result <= now:

            result += timedelta(
                days=1
            )

        return result

    except ValueError:
        pass

    return None


# =========================================================
# Registry
# =========================================================

register(
    "create_reminder",
    create_reminder,
)

register(
    "list_reminders",
    list_reminders,
)

register(
    "cancel_reminder",
    cancel_reminder,
)


# =========================================================
# Start
# =========================================================

start_reminder_scheduler()