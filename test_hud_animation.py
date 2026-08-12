"""
JARVIS PRO
HUD Animation Test

UI-only simulator.

Does NOT connect to JARVIS.
"""

import time

from hud.manager import hud


def main():

    print()
    print("=== HUD ANIMATION TEST ===")
    print()

    states = [
        ("idle", 3),
        ("listening", 4),
        ("thinking", 4),
        ("speaking", 4),
        ("executing", 4),
        ("error", 4),
        ("idle", 3),
    ]

    for state, duration in states:

        print(
            f"[HUD TEST] State: {state}"
        )

        if state == "idle":
            hud.idle()

        elif state == "listening":
            hud.listening()

        elif state == "thinking":
            hud.thinking()

        elif state == "speaking":
            hud.speaking()

        elif state == "executing":
            hud.executing(
                "HUD animation test"
            )

        elif state == "error":
            hud.error(
                "HUD animation test error"
            )

        time.sleep(
            duration
        )

    print()
    print("=== HUD ANIMATION TEST COMPLETE ===")


if __name__ == "__main__":
    main()