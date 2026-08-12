"""
JARVIS PRO
HUD Notification Visualization Test

Standalone HUD test.
Does NOT connect to JARVIS core.
"""

import time

from hud.manager import hud


def main():

    print()
    print("=== HUD NOTIFICATION TEST ===")
    print()

    # -------------------------------------------------
    # Normal notification
    # -------------------------------------------------

    print("[HUD NOTIFICATION] Normal message")

    hud.notify(
        "HUD notification test started."
    )

    time.sleep(4)

    # -------------------------------------------------
    # Second notification
    # -------------------------------------------------

    print("[HUD NOTIFICATION] Task message")

    hud.notify(
        "Developer Generator task completed."
    )

    time.sleep(4)

    # -------------------------------------------------
    # Error notification
    # -------------------------------------------------

    print("[HUD NOTIFICATION] Error message")

    hud.error(
        "Example HUD error notification."
    )

    time.sleep(4)

    # -------------------------------------------------
    # Return to normal
    # -------------------------------------------------

    print("[HUD NOTIFICATION] Clearing notification")

    hud.idle()

    time.sleep(2)

    print()
    print("=== HUD NOTIFICATION TEST COMPLETE ===")


if __name__ == "__main__":
    main()