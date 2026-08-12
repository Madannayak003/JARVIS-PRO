"""
JARVIS PRO
HUD Task Visualization Test

Standalone HUD test.
Does NOT connect to JARVIS core.
"""

import time

from hud.manager import hud


def main():

    print()
    print("=== HUD TASK VISUALIZATION TEST ===")
    print()

    # -------------------------------------------------
    # Start task
    # -------------------------------------------------

    print("[HUD TASK TEST] Starting task...")

    hud.task_started(
        "Developer Generator"
    )

    time.sleep(2)

    # -------------------------------------------------
    # Executing
    # -------------------------------------------------

    print("[HUD TASK TEST] Executing...")

    hud.executing(
        "Developer Generator"
    )

    time.sleep(4)

    # -------------------------------------------------
    # Finish
    # -------------------------------------------------

    print("[HUD TASK TEST] Finishing...")

    hud.task_finished(
        "Developer Generator"
    )

    time.sleep(3)

    # -------------------------------------------------
    # Second task - error
    # -------------------------------------------------

    print("[HUD TASK TEST] Starting error test...")

    hud.task_started(
        "Test Task"
    )

    time.sleep(2)

    hud.executing(
        "Test Task"
    )

    time.sleep(2)

    hud.task_failed(
        "Test Task",
        "Example HUD task error"
    )

    time.sleep(3)

    # -------------------------------------------------
    # Return idle
    # -------------------------------------------------

    print("[HUD TASK TEST] Returning to idle...")

    hud.idle()

    time.sleep(2)

    print()
    print("=== HUD TASK VISUALIZATION TEST COMPLETE ===")


if __name__ == "__main__":
    main()