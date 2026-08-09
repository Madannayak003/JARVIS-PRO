import re
from datetime import datetime, timedelta


def memory_route(command):

    command = command.lower().strip()

    # =================================================
    # NOTES
    # =================================================

    match = re.match(
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

    if match:

        text = match.group(1).strip()

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

    # -------------------------------------------------
    # Remind me at TIME
    #
    # Examples:
    #   remind me at 10:30 PM to call John
    #   remind me at 10:30 p.m. to call John
    #   remind me at 10 PM to call John
    #   remind me at 10 p.m. to call John
    # -------------------------------------------------

    match = re.match(
        r"^remind\s+me\s+at\s+"
        r"(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?))"
        r"\s+(?:to\s+)?(.+)$",
        command,
        re.IGNORECASE,
    )

    if match:

        time_text = match.group(1).strip()
        text = match.group(2).strip()

        time_text = (
            time_text
            .replace(".", "")
            .upper()
        )

        target = _parse_clock_time(
            time_text
        )

        if target and text:

            print(
                "[MEMORY ROUTER] Creating reminder:",
                text,
                "->",
                target.isoformat(),
            )

            return [
                {
                    "action": "create_reminder",
                    "text": text,
                    "remind_at": target.isoformat(),
                }
            ]

    # -------------------------------------------------
    # Remind me in X minutes
    # -------------------------------------------------

    match = re.match(
        r"^remind\s+me\s+in\s+"
        r"(\d+)\s+"
        r"(minute|minutes|min|mins)"
        r"(?:\s+to)?\s+(.+)$",
        command,
        re.IGNORECASE,
    )

    if match:

        minutes = int(match.group(1))
        text = match.group(3).strip()

        target = (
            datetime.now()
            + timedelta(minutes=minutes)
        )

        print(
            "[MEMORY ROUTER] Creating reminder:",
            text,
            "->",
            target.isoformat(),
        )

        return [
            {
                "action": "create_reminder",
                "text": text,
                "remind_at": target.isoformat(),
            }
        ]

    # -------------------------------------------------
    # List reminders
    # -------------------------------------------------

    if command in (
        "list reminders",
        "list my reminders",
        "show reminders",
        "show my reminders",
        "what are my reminders",
        "read my reminders",
    ):

        print("[MEMORY ROUTER] Listing reminders")

        return [
            {
                "action": "list_reminders"
            }
        ]

    return None


# =====================================================
# Clock Parser
# =====================================================

def _parse_clock_time(
    value,
    tomorrow=False,
):

    try:

        value = (
            value
            .replace(".", "")
            .upper()
            .strip()
        )

        formats = (
            "%I:%M %p",
            "%I %p",
        )

        parsed = None

        for fmt in formats:

            try:

                parsed = datetime.strptime(
                    value,
                    fmt,
                )

                break

            except ValueError:

                continue

        if parsed is None:

            print(
                f"[MEMORY ROUTER] Invalid time: {value}"
            )

            return None

        now = datetime.now()

        target = now.replace(
            hour=parsed.hour,
            minute=parsed.minute,
            second=0,
            microsecond=0,
        )

        if tomorrow:

            target += timedelta(days=1)

        elif target <= now:

            target += timedelta(days=1)

        return target

    except Exception as e:

        print(
            f"[MEMORY ROUTER ERROR] {e}"
        )

        return None