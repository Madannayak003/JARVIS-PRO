import re
from datetime import datetime, timedelta


def memory_route(command):

    command = command.lower().strip()

    # =================================================
    # NOTES
    # =================================================

    note_match = re.match(
        r"^(?:"
        r"make\s+(?:a\s+)?note"
        r"|take\s+(?:a\s+)?note"
        r"|note"
        r")"
        r"(?:\s+(?:to|that))?"
        r"\s+(.+)$",
        command,
        re.IGNORECASE,
    )

    if note_match:

        text = note_match.group(1).strip()

        if text:

            print(
                f"[MEMORY ROUTER] Creating note: {text}"
            )

            return [
                {
                    "action": "create_note",
                    "text": text,
                }
            ]

    # -------------------------------------------------
    # List notes
    # -------------------------------------------------

    if command in (
        "list notes",
        "list my notes",
        "show notes",
        "show my notes",
        "what are my notes",
        "read my notes",
    ):

        print("[MEMORY ROUTER] Listing notes")

        return [
            {
                "action": "list_notes"
            }
        ]

    # -------------------------------------------------
    # Clear notes
    # -------------------------------------------------

    if command in (
        "clear notes",
        "clear my notes",
        "delete notes",
        "delete my notes",
        "remove notes",
    ):

        print("[MEMORY ROUTER] Clearing notes")

        return [
            {
                "action": "clear_notes"
            }
        ]

    # =================================================
    # REMINDERS
    # =================================================

    # -----------------------------------------------
    # Remind me in X minutes/hours
    #
    # Example:
    # remind me in 5 minutes to call John
    # remind me in 2 hours to check the oven
    # -----------------------------------------------

    match = re.match(
        r"^remind\s+me\s+in\s+"
        r"(\d+)\s+"
        r"(second|seconds|minute|minutes|hour|hours)"
        r"\s+(?:to\s+)?(.+)$",
        command,
        re.IGNORECASE,
    )

    if match:

        amount = int(match.group(1))
        unit = match.group(2).lower()
        text = match.group(3).strip()

        if unit.startswith("second"):
            target = datetime.now() + timedelta(
                seconds=amount
            )

        elif unit.startswith("minute"):
            target = datetime.now() + timedelta(
                minutes=amount
            )

        else:
            target = datetime.now() + timedelta(
                hours=amount
            )

        remind_at = target.isoformat()

        print(
            f"[MEMORY ROUTER] Creating reminder: "
            f"{text} -> {remind_at}"
        )

        return [
            {
                "action": "create_reminder",
                "text": text,
                "remind_at": remind_at,
            }
        ]

    # -----------------------------------------------
    # Remind me at TIME
    #
    # Example:
    # remind me at 10:30 PM to call John
    # remind me at 8 AM to take medicine
    # -----------------------------------------------

    match = re.match(
        r"^remind\s+me\s+at\s+"
        r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))"
        r"\s+(?:to\s+)?(.+)$",
        command,
        re.IGNORECASE,
    )

    if match:

        time_text = match.group(1).strip().upper()
        text = match.group(2).strip()

        target = _parse_clock_time(
            time_text
        )

        if target:

            print(
                f"[MEMORY ROUTER] Creating reminder: "
                f"{text} -> {target.isoformat()}"
            )

            return [
                {
                    "action": "create_reminder",
                    "text": text,
                    "remind_at": target.isoformat(),
                }
            ]

    # -----------------------------------------------
    # Remind me tomorrow at TIME
    #
    # Example:
    # remind me tomorrow at 10 PM to call John
    # -----------------------------------------------

    match = re.match(
        r"^remind\s+me\s+tomorrow\s+at\s+"
        r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))"
        r"\s+(?:to\s+)?(.+)$",
        command,
        re.IGNORECASE,
    )

    if match:

        time_text = match.group(1).strip().upper()
        text = match.group(2).strip()

        target = _parse_clock_time(
            time_text,
            tomorrow=True,
        )

        if target:

            print(
                f"[MEMORY ROUTER] Creating reminder: "
                f"{text} -> {target.isoformat()}"
            )

            return [
                {
                    "action": "create_reminder",
                    "text": text,
                    "remind_at": target.isoformat(),
                }
            ]

    # -----------------------------------------------
    # List reminders
    # -----------------------------------------------

    if command in (
        "list reminders",
        "list my reminders",
        "show reminders",
        "show my reminders",
        "what are my reminders",
    ):

        print(
            "[MEMORY ROUTER] Listing reminders"
        )

        return [
            {
                "action": "list_reminders"
            }
        ]

    # -----------------------------------------------
    # Cancel reminder by ID
    #
    # Example:
    # cancel reminder 3
    # cancel reminder number 3
    # -----------------------------------------------

    match = re.match(
        r"^cancel\s+(?:reminder\s+)?"
        r"(?:number\s+)?(\d+)$",
        command,
        re.IGNORECASE,
    )

    if match:

        reminder_id = int(
            match.group(1)
        )

        print(
            f"[MEMORY ROUTER] Cancelling reminder: "
            f"{reminder_id}"
        )

        return [
            {
                "action": "cancel_reminder",
                "id": reminder_id,
            }
        ]

    return None


# =================================================
# Clock Parser
# =================================================

def _parse_clock_time(
    value,
    tomorrow=False,
):

    try:

        formats = (
            "%I:%M %p",
            "%I %p",
        )

        parsed = None

        for fmt in formats:

            try:

                parsed = datetime.strptime(
                    value.upper(),
                    fmt,
                )

                break

            except ValueError:

                continue

        if parsed is None:
            return None

        now = datetime.now()

        target = now.replace(
            hour=parsed.hour,
            minute=parsed.minute,
            second=0,
            microsecond=0,
        )

        if tomorrow:

            target += timedelta(
                days=1
            )

        elif target <= now:

            target += timedelta(
                days=1
            )

        return target

    except Exception as e:

        print(
            f"[MEMORY ROUTER ERROR] {e}"
        )

        return None