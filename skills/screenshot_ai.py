import os

from core.registry import register
from voice.manager import speak

from ai.core.service import ai_service

from core.paths import SCREENSHOTS


def screenshot_ai(data):

    files = sorted(

        SCREENSHOTS.glob("*.png"),

        key=os.path.getmtime

    )

    if not files:

        speak("No screenshots found.")

        return True

    latest = files[-1]

    print(
        "[SCREENSHOT AI] Analyzing:",
        latest
    )

    response = ai_service.generate(

        prompt=str(latest),

        system_prompt="Describe this screenshot.",

        capability="conversation",

    )

    if not response.success:

        print(
            "[SCREENSHOT AI] Generation failed:",
            response.error,
        )

        speak(
            "I could not analyze the screenshot."
        )

        return True

    print(
        "[SCREENSHOT AI] Provider:",
        response.provider,
    )

    print(
        "[SCREENSHOT AI] Model:",
        response.model,
    )

    speak(response.text)

    return True


register(
    "screenshot_ai",
    screenshot_ai
)