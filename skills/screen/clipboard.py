import pyperclip

from core.registry import register
from voice.manager import speak

from ai.core.service import ai_service


def clipboard(data):

    text = pyperclip.paste()

    mode = data.get("mode", "read")

    # --------------------------------------------------
    # Read
    # --------------------------------------------------

    if mode == "read":

        speak(text[:300])

        return True

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    if mode == "summary":

        response = ai_service.generate(

            prompt=text,

            system_prompt="Summarize this.",

            capability="conversation",

        )

        if not response.success:

            print(
                "[CLIPBOARD AI] Generation failed:",
                response.error,
            )

            return True

        print(
            "[CLIPBOARD AI] Provider:",
            response.provider,
        )

        print(
            "[CLIPBOARD AI] Model:",
            response.model,
        )

        speak(response.text)

        return True

    # --------------------------------------------------
    # Explain
    # --------------------------------------------------

    if mode == "explain":

        response = ai_service.generate(

            prompt=text,

            system_prompt="Explain this.",

            capability="conversation",

        )

        if not response.success:

            print(
                "[CLIPBOARD AI] Generation failed:",
                response.error,
            )

            return True

        print(
            "[CLIPBOARD AI] Provider:",
            response.provider,
        )

        print(
            "[CLIPBOARD AI] Model:",
            response.model,
        )

        speak(response.text)

        return True

    return True


register(
    "clipboard",
    clipboard
)