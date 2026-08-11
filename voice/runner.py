"""
JARVIS PRO
Voice Mode Launcher

Selects exactly ONE voice architecture.

ONLINE:
    Uses the existing online JARVIS runner.

OFFLINE:
    Uses the completely isolated offline runner.

This file does NOT modify either voice system.
"""

from voice.mode import get_mode


def run():
    mode = get_mode()

    print(f"[VOICE LAUNCHER] Mode: {mode}")

    if mode == "offline":

        print(
            "[VOICE LAUNCHER] "
            "Starting isolated offline voice..."
        )

        from voice.offline.offline_runner import run as offline_run

        return offline_run()

    # -------------------------------------------------
    # ONLINE
    # -------------------------------------------------

    print(
        "[VOICE LAUNCHER] "
        "Starting existing online voice..."
    )

    from voice.online_runner import run as online_run

    return online_run()


if __name__ == "__main__":
    run()