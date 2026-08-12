"""
JARVIS PRO
HUD Runtime Test

Standalone test.
Does not connect to JARVIS.
"""

from hud.runtime import hud_runtime


def main():

    print()
    print("=== HUD RUNTIME TEST ===")
    print()

    print(
        "[TEST] Before:",
        hud_runtime.is_running()
    )

    hud_runtime.start()

    print(
        "[TEST] After start:",
        hud_runtime.is_running()
    )

    hud_runtime.stop()

    print(
        "[TEST] After stop:",
        hud_runtime.is_running()
    )

    print()
    print("=== HUD RUNTIME TEST COMPLETE ===")
    print()


if __name__ == "__main__":
    main()