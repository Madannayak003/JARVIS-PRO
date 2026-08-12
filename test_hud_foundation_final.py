"""
JARVIS PRO
Final HUD Foundation Test

Standalone test only.
Does NOT connect to JARVIS core.
"""

import time

from hud.manager import hud


def show_state(label):

    state = hud.state

    print(
        f"[HUD FINAL] {label} | "
        f"status={state.status} | "
        f"voice={state.voice_mode} | "
        f"task={state.current_task} | "
        f"task_status={state.task_status}"
    )


def main():

    print()
    print("==========================================")
    print("       JARVIS HUD FOUNDATION TEST")
    print("==========================================")
    print()

    # -------------------------------------------------
    # IDLE
    # -------------------------------------------------

    hud.idle()

    show_state("IDLE")

    time.sleep(2)

    # -------------------------------------------------
    # LISTENING
    # -------------------------------------------------

    hud.listening()

    show_state("LISTENING")

    time.sleep(2)

    # -------------------------------------------------
    # THINKING
    # -------------------------------------------------

    hud.thinking()

    show_state("THINKING")

    time.sleep(2)

    # -------------------------------------------------
    # AI MODEL
    # -------------------------------------------------

    hud.ai_model(
        "ollama",
        "jarvis"
    )

    show_state("AI MODEL")

    time.sleep(2)

    # -------------------------------------------------
    # TASK START
    # -------------------------------------------------

    hud.task_started(
        "Developer Generator"
    )

    show_state("TASK STARTED")

    time.sleep(2)

    # -------------------------------------------------
    # EXECUTING
    # -------------------------------------------------

    hud.executing(
        "Developer Generator"
    )

    show_state("EXECUTING")

    time.sleep(3)

    # -------------------------------------------------
    # SYSTEM TELEMETRY
    # -------------------------------------------------

    hud.system_update(
        {
            "cpu": 25,
            "ram": 48,
            "battery": 87
        }
    )

    show_state("TELEMETRY")

    time.sleep(3)

    # -------------------------------------------------
    # TASK FINISHED
    # -------------------------------------------------

    hud.task_finished(
        "Developer Generator"
    )

    show_state("TASK FINISHED")

    time.sleep(2)

    # -------------------------------------------------
    # NOTIFICATION
    # -------------------------------------------------

    hud.notify(
        "HUD foundation test completed successfully."
    )

    show_state("NOTIFICATION")

    time.sleep(4)

    # -------------------------------------------------
    # FINAL IDLE
    # -------------------------------------------------

    hud.idle()

    show_state("FINAL IDLE")

    time.sleep(2)

    print()
    print("==========================================")
    print("     HUD FOUNDATION TEST COMPLETE")
    print("==========================================")
    print()


if __name__ == "__main__":
    main()