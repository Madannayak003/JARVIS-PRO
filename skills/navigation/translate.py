"""
=============================================================
JARVIS PRO — GOOGLE TRANSLATE SKILL
=============================================================

Provides Google Translate opening.

Google Translate uses its normal web interface, so no API key
is required for this skill.
"""

import webbrowser

from core.registry import register
from voice.manager import speak
from urllib.parse import quote_plus

GOOGLE_TRANSLATE_URL = "https://translate.google.com/"


# =============================================================
# OPEN GOOGLE TRANSLATE
# =============================================================

def translate_open(data=None):
    try:

        opened = webbrowser.open_new_tab(
            GOOGLE_TRANSLATE_URL
        )

        if opened:
            speak("Opening Google Translate.")
            return True

        speak("I could not open Google Translate.")
        return False

    except Exception as error:

        print(
            f"[TRANSLATE ERROR] {error}"
        )

        speak(
            "I could not open Google Translate."
        )

        return False
    
# =============================================================
# TRANSLATE TEXT
# =============================================================

def translate_text(data=None):
    data = data or {}

    text = str(
        data.get("text", "")
    ).strip()

    target = str(
        data.get("target", "")
    ).strip()

    if not text:
        speak("Please tell me what to translate.")
        return False

    if not target:
        speak("Please tell me the target language.")
        return False

    encoded_text = quote_plus(text)
    encoded_target = quote_plus(target)

    url = (
        "https://translate.google.com/"
        "?sl=auto"
        f"&tl={encoded_target}"
        f"&text={encoded_text}"
        "&op=translate"
    )

    try:

        opened = webbrowser.open_new_tab(url)

        if opened:
            speak(
                f"Opening translation to {target}."
            )
            return True

        speak(
            "I could not open Google Translate."
        )
        return False

    except Exception as error:

        print(
            f"[TRANSLATE ERROR] {error}"
        )

        speak(
            "I could not open Google Translate."
        )

        return False


# =============================================================
# REGISTRATION
# =============================================================

register(
    "translate_open",
    translate_open,
)

register(
    "translate_text",
    translate_text,
)