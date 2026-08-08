import datetime
import pyautogui

from core.registry import register
from voice.manager import speak

from core.paths import SCREENSHOTS


def screenshot(data):

    filename = datetime.datetime.now().strftime(
        "Screenshot_%Y%m%d_%H%M%S.png"
    )

    filepath = SCREENSHOTS / filename

    pyautogui.screenshot(str(filepath))

    print(f"\nSaved : {filepath}")

    speak("Screenshot captured successfully.")

    return True


register(
    "screenshot",
    screenshot
)