"""
JARVIS PRO
Email Skill

Responsibilities:
- Send emails through Gmail
- Provide JARVIS voice feedback
"""

from core.registry import register
from voice.manager import speak

from services.gmail_service import send_email as gmail_send_email


# =========================================================
# Send Email
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

        speak("Please provide the recipient email address.")

        return False

    if not subject:

        speak("Please provide the email subject.")

        return False

    if not body:

        speak("Please provide the email message.")

        return False

    print(f"[EMAIL] To: {recipient}")
    print(f"[EMAIL] Subject: {subject}")
    print(f"[EMAIL] Body: {body}")

    try:

        gmail_send_email(
            recipient=recipient,
            subject=subject,
            body=body
        )

    except Exception as error:

        print(f"[EMAIL ERROR] {error}")

        speak("I could not send the email.")

        return False

    print("[EMAIL] Email sent successfully.")

    speak("Email sent successfully.")

    return True


# =========================================================
# Register Skills
# =========================================================

register(
    "send_email",
    send_email
)


print("[EMAIL] Skill loaded")