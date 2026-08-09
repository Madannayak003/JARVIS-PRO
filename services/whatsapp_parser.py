import re
from datetime import datetime, timedelta


# =========================================================
# Scheduled WhatsApp Message Parser
# =========================================================

def parse_scheduled_whatsapp(command):

    command = command.strip()

    now = datetime.now()

    # =====================================================
    # IN X SECONDS / MINUTES / HOURS
    #
    # Examples:
    #
    # send whatsapp to mom in 30 minutes saying I'm on the way
    # send whatsapp to dad in 2 hours saying I will call
    # send whatsapp to mom in 10 seconds saying hello
    # =====================================================

    match = re.fullmatch(

        r"send\s+whatsapp\s+to\s+"
        r"(.+?)"
        r"\s+in\s+"
        r"(\d+)\s+"
        r"(seconds?|minutes?|hours?)"
        r"\s+saying\s+"
        r"(.+)",

        command,

        re.IGNORECASE,
    )

    if match:

        contact = match.group(1).strip()

        amount = int(
            match.group(2)
        )

        unit = match.group(3).lower()

        message = match.group(4).strip()

        if not contact or not message:
            return None

        if unit.startswith("second"):

            target = now + timedelta(
                seconds=amount
            )

        elif unit.startswith("minute"):

            target = now + timedelta(
                minutes=amount
            )

        else:

            target = now + timedelta(
                hours=amount
            )

        return {
            "contact": contact,
            "message": message,
            "send_at": target.isoformat(),
        }

    # =====================================================
    # TOMORROW AT TIME
    #
    # Examples:
    #
    # send whatsapp to dad tomorrow at 9 AM saying I'll call you
    # send whatsapp to mom tomorrow at 10:30 PM saying good night
    # =====================================================

    match = re.fullmatch(

        r"send\s+whatsapp\s+to\s+"
        r"(.+?)"
        r"\s+tomorrow\s+at\s+"
        r"(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?))"
        r"\s+saying\s+"
        r"(.+)",

        command,

        re.IGNORECASE,
    )

    if match:

        contact = match.group(1).strip()

        time_text = match.group(2).strip()

        message = match.group(3).strip()

        if not contact or not message:
            return None

        time_text = (
            time_text
            .replace(".", "")
            .upper()
            .strip()
        )

        target = _parse_schedule_time(
            time_text,
            tomorrow=True,
        )

        if target is None:
            return None

        return {
            "contact": contact,
            "message": message,
            "send_at": target.isoformat(),
        }

    # =====================================================
    # TODAY AT TIME
    #
    # Examples:
    #
    # send whatsapp to mom today at 8 PM saying I'm home
    # =====================================================

    match = re.fullmatch(

        r"send\s+whatsapp\s+to\s+"
        r"(.+?)"
        r"\s+today\s+at\s+"
        r"(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?))"
        r"\s+saying\s+"
        r"(.+)",

        command,

        re.IGNORECASE,
    )

    if match:

        contact = match.group(1).strip()

        time_text = match.group(2).strip()

        message = match.group(3).strip()

        if not contact or not message:
            return None

        time_text = (
            time_text
            .replace(".", "")
            .upper()
            .strip()
        )

        target = _parse_schedule_time(
            time_text,
            tomorrow=False,
        )

        if target is None:
            return None

        return {
            "contact": contact,
            "message": message,
            "send_at": target.isoformat(),
        }

    return None


# =========================================================
# Schedule Clock Parser
# =========================================================

def _parse_schedule_time(
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
                    value,
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

            # "today at 8 PM" when 8 PM already passed
            # should not accidentally schedule yesterday.
            return None

        return target

    except Exception as e:

        print(
            f"[WHATSAPP SCHEDULE PARSER ERROR] {e}"
        )

        return None


# =========================================================
# Normal WhatsApp Message Parser
# =========================================================

def parse_whatsapp(command):

    command = command.strip()

    patterns = [

        # send whatsapp to John saying hello
        (
            r"send\s+whatsapp\s+to\s+(.+?)"
            r"\s+saying\s+(.+)"
        ),

        # send whatsapp message to John saying hello
        (
            r"send\s+whatsapp\s+message\s+to\s+(.+?)"
            r"\s+saying\s+(.+)"
        ),

        # send message to John saying hello
        (
            r"send\s+message\s+to\s+(.+?)"
            r"\s+saying\s+(.+)"
        ),

        # send whatsapp message to John hello
        (
            r"send\s+whatsapp\s+message\s+to\s+(.+?)"
            r"\s+(.+)"
        ),

        # send message to John hello
        (
            r"send\s+message\s+to\s+(.+?)"
            r"\s+(.+)"
        ),

        # send whatsapp to John hello
        (
            r"send\s+whatsapp\s+to\s+(.+?)"
            r"\s+(.+)"
        ),
    ]

    for pattern in patterns:

        match = re.fullmatch(
            pattern,
            command,
            re.IGNORECASE,
        )

        if match:

            contact = match.group(1).strip()

            message = match.group(2).strip()

            if contact and message:

                return {
                    "contact": contact,
                    "message": message,
                }

    return None