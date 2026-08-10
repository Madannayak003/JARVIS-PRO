"""
JARVIS PRO
Live Screen Vision Skill

Analyzes the current desktop directly from memory.

Unlike screenshot_ai, this skill does NOT:

- save a screenshot
- search for a previous screenshot
- analyze a PNG from disk

It captures the current screen once and sends the
image directly to the AI vision system.

The successful analysis is also stored in the
ScreenContextManager for later contextual use.
"""

from core.registry import register

from ai.core.service import ai_service

from skills.screen.screen_vision import screen_vision

from brain.screen_context import screen_context


# =========================================================
# Live Screen Analysis
# =========================================================

def screen_vision_analyze(data=None):
    """
    Analyze the current computer screen.

    The screen is captured directly into memory and
    passed to the multimodal AI system.

    The resulting analysis is stored as screen context.
    """

    # -----------------------------------------------------
    # Capture current screen
    # -----------------------------------------------------

    image = screen_vision.capture()

    if image is None:

        print(
            "[SCREEN VISION] Unable to capture current screen."
        )

        return (
            "I couldn't access the current screen."
        )

    # -----------------------------------------------------
    # AI Analysis
    # -----------------------------------------------------

    try:

        response = ai_service.generate(

            prompt=(
                "Look at my current computer screen and "
                "tell me naturally what I am looking at. "
                "Identify the main application or window, "
                "important visible content, useful text, "
                "and anything relevant to what I am doing. "
                "Do not describe every small visual detail. "
                "Focus on what would actually help me."
            ),

            system_prompt=(
                "You are JARVIS PRO's live screen vision "
                "assistant. Analyze the provided current "
                "desktop image accurately. Respond naturally "
                "like a professional personal assistant "
                "speaking to the user. Do not sound robotic "
                "or like an object detector. Only describe "
                "information that is actually visible."
            ),

            capability="screen_vision",

            images=[image],
        )

    except Exception as e:

        print(
            f"[SCREEN VISION AI ERROR] {e}"
        )

        return (
            "I couldn't analyze the current screen."
        )

    # -----------------------------------------------------
    # AI Failure
    # -----------------------------------------------------

    if not response.success:

        print(
            "[SCREEN VISION AI] Generation failed:",
            response.error,
        )

        return (
            "I couldn't analyze the current screen."
        )

    # -----------------------------------------------------
    # Diagnostics
    # -----------------------------------------------------

    print(
        "[SCREEN VISION AI] Provider:",
        response.provider,
    )

    print(
        "[SCREEN VISION AI] Model:",
        response.model,
    )

    # -----------------------------------------------------
    # Empty response
    # -----------------------------------------------------

    if not response.text:

        return (
            "I couldn't get a useful description "
            "of the current screen."
        )

    # -----------------------------------------------------
    # Final Analysis
    # -----------------------------------------------------

    analysis = response.text.strip()

    # -----------------------------------------------------
    # Store Screen Context
    #
    # IMPORTANT:
    # The existing captured image is NOT captured again.
    # Only the AI's understanding is stored.
    # -----------------------------------------------------

    try:

        screen_context.set_context({

            "analysis": analysis,

            "provider": response.provider,

            "model": response.model,

            "resolution": (
                image.size
                if hasattr(image, "size")
                else None
            ),

            "source": "live_screen",

        })

        print(
            "[SCREEN CONTEXT] Updated."
        )

    except Exception as e:

        # Context storage must never break
        # the existing screen vision feature.

        print(
            f"[SCREEN CONTEXT ERROR] {e}"
        )

    # -----------------------------------------------------
    # Return natural response
    # -----------------------------------------------------

    return analysis


# =========================================================
# Registry
# =========================================================

register(
    "screen_vision_analyze",
    screen_vision_analyze,
    category="screen",
)

print(
    "[SCREEN VISION SKILL] Registered."
)