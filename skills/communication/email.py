"""
JARVIS PRO
Email Skill

Responsibilities:
- Send emails through Gmail
- Manage multi-step email composition
- Provide JARVIS voice feedback
"""

from core.registry import register
from voice.manager import speak

from services.gmail_service import send_email as gmail_send_email

from services.email_contact_manager import (
    resolve_email_contact,
)


# =========================================================
# Pending Email Draft
# =========================================================

_PENDING_EMAIL = None


def has_pending_email():
    """
    Return True when JARVIS is waiting for an email field.
    """

    return _PENDING_EMAIL is not None


def clear_email_draft():
    """
    Clear the current pending email draft.
    """

    global _PENDING_EMAIL

    _PENDING_EMAIL = None


def start_email_draft(recipient):
    """
    Start a new multi-step email draft.
    """

    global _PENDING_EMAIL

    recipient = str(
        recipient or ""
    ).strip()

    recipient = resolve_email_contact(
        recipient
    )

    if not recipient:

        speak(
            "Please provide the recipient email address."
        )

        return False

    _PENDING_EMAIL = {
        "recipient": recipient,
        "subject": "",
        "body": "",
        "stage": "subject",
    }

    print(
        "[EMAIL] Draft started."
    )

    print(
        f"[EMAIL] Recipient: {recipient}"
    )

    speak(
        "What is the subject?"
    )

    return True


def handle_email_reply(command):
    """
    Handle the next response while composing an email.
    """

    global _PENDING_EMAIL

    if _PENDING_EMAIL is None:
        return False

    command = str(
        command or ""
    ).strip()

    if not command:
        return True

    # -----------------------------------------------------
    # Subject
    # -----------------------------------------------------

    if _PENDING_EMAIL["stage"] == "subject":

        _PENDING_EMAIL["subject"] = command

        _PENDING_EMAIL["stage"] = "body"

        print(
            f"[EMAIL] Subject: {command}"
        )

        speak(
            "What should I say?"
        )

        return True

    # -----------------------------------------------------
    # Body
    # -----------------------------------------------------

    if _PENDING_EMAIL["stage"] == "body":

        _PENDING_EMAIL["body"] = command

        recipient = _PENDING_EMAIL["recipient"]
        subject = _PENDING_EMAIL["subject"]
        body = _PENDING_EMAIL["body"]

        print(
            f"[EMAIL] To: {recipient}"
        )

        print(
            f"[EMAIL] Subject: {subject}"
        )

        print(
            f"[EMAIL] Body: {body}"
        )

        try:

            gmail_send_email(
                recipient=recipient,
                subject=subject,
                body=body,
            )

        except Exception as error:

            print(
                f"[EMAIL ERROR] {error}"
            )

            clear_email_draft()

            speak(
                "I could not send the email."
            )

            return False

        clear_email_draft()

        print(
            "[EMAIL] Email sent successfully."
        )

        speak(
            "Email sent successfully."
        )

        return True

    return False


# =========================================================
# Send Email Action
# =========================================================

def send_email(data=None):

    data = data or {}

    recipient = str(
        data.get("recipient", "")
    ).strip()

    subject = str(
        data.get("subject", "")
    ).strip()

    body = str(
        data.get("body", "")
    ).strip()

    if not recipient:

        speak(
            "Please provide the recipient email address."
        )

        return False

    # -----------------------------------------------------
    # Complete email supplied directly
    # -----------------------------------------------------

    if subject and body:

        print(
            f"[EMAIL] To: {recipient}"
        )

        print(
            f"[EMAIL] Subject: {subject}"
        )

        print(
            f"[EMAIL] Body: {body}"
        )

        try:

            gmail_send_email(
                recipient=recipient,
                subject=subject,
                body=body,
            )

        except Exception as error:

            print(
                f"[EMAIL ERROR] {error}"
            )

            speak(
                "I could not send the email."
            )

            return False

        print(
            "[EMAIL] Email sent successfully."
        )

        speak(
            "Email sent successfully."
        )

        return True

    # -----------------------------------------------------
    # Start multi-step composition
    # -----------------------------------------------------

    return start_email_draft(
        recipient
    )


# =========================================================
# Register Skills
# =========================================================

register(
    "send_email",
    send_email
)


print(
    "[EMAIL] Skill loaded"
)