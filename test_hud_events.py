import time

from hud.manager import hud


def main():

    print()
    print("=== HUD EVENT VISUALIZATION TEST ===")
    print()

    states = [
        ("idle", 2),
        ("listening", 3),
        ("thinking", 3),
        ("speaking", 3),
        ("executing", 3),
        ("error", 3),
        ("idle", 2),
    ]

    for state, duration in states:

        print(f"[HUD EVENT TEST] {state.upper()}")

        if state == "idle":
            hud.idle()

        elif state == "listening":
            hud.listening()

        elif state == "thinking":
            hud.thinking()

        elif state == "speaking":
            hud.speaking()

        elif state == "executing":
            hud.executing("HUD event test")

        elif state == "error":
            hud.error("HUD event visualization test")

        time.sleep(duration)

    print()
    print("=== HUD EVENT VISUALIZATION TEST COMPLETE ===")


if __name__ == "__main__":
    main()