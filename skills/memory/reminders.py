"""
JARVIS PRO
Reminder Skill

Handles creation, listing and cancellation of reminders.
"""

import json
from pathlib import Path
from datetime import datetime

from core.registry import register
from voice.manager import speak


# =========================================================
# Storage
# =========================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

REMINDERS_FILE = DATA_DIR / "reminders.json"


# =========================================================
# Storage Helpers
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

    reminder = {
        "id": len(reminders) + 1,
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

        if str(reminder.get("id")) == str(reminder_id):

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