"""
JARVIS PRO
Screen Vision Engine

Captures the current desktop directly in memory
for multimodal AI analysis.

This does NOT save screenshots to disk.
"""

import pyautogui


class ScreenVision:

    # ==================================================
    # Capture Current Screen
    # ==================================================

    def capture(self):

        try:

            image = pyautogui.screenshot()

            print(
                "[SCREEN VISION] Current screen captured."
            )

            return image

        except Exception as e:

            print(
                f"[SCREEN VISION ERROR] {e}"
            )

            return None


# ======================================================
# Shared Screen Vision
# ======================================================

screen_vision = ScreenVision()