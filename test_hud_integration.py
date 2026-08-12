"""
JARVIS PRO
HUD Integration Test

Tests the real HUD integration boundary.

This test does NOT connect to JARVIS core.
"""

from hud.integration import HUDIntegration
from hud.manager import hud


def show_state(label):

    state = hud.state

    print(
        f"[HUD TEST] {label}: "
        f"status={state.status}, "
        f"voice={state.voice_mode}, "
        f"task={state.current_task}, "
        f"task_status={state.task_status}, "
        f"listening={state.listening}, "
        f"thinking={state.thinking}, "
        f"speaking={state.speaking}"
    )


def main():

    print()
    print("=== HUD INTEGRATION ON TEST ===")
    print()

    print(
        "[HUD INTEGRATION] Enabled:",
        HUDIntegration.enabled()
    )

    if not HUDIntegration.enabled():

        print()
        print(
            "[ERROR] HUD integration is disabled."
        )

        return

    # -------------------------------------------------
    # Voice mode
    # -------------------------------------------------

    HUDIntegration.voice_mode(
        "offline"
    )

    show_state("VOICE MODE")

    # -------------------------------------------------
    # Listening
    # -------------------------------------------------

    HUDIntegration.listening()

    show_state("LISTENING")

    # -------------------------------------------------
    # Thinking
    # -------------------------------------------------

    HUDIntegration.thinking()

    show_state("THINKING")

    # -------------------------------------------------
    # AI model
    # -------------------------------------------------

    HUDIntegration.ai_model(
        "ollama",
        "jarvis"
    )

    show_state("AI MODEL")

    # -------------------------------------------------
    # Task
    # -------------------------------------------------

    HUDIntegration.task_started(
        "Developer Generator"
    )

    show_state("TASK STARTED")

    # -------------------------------------------------
    # Executing
    # -------------------------------------------------

    HUDIntegration.executing(
        "Developer Generator"
    )

    show_state("EXECUTING")

    # -------------------------------------------------
    # Telemetry
    # -------------------------------------------------

    HUDIntegration.system_update(
        {
            "cpu": 25,
            "ram": 48,
            "battery": 87
        }
    )

    show_state("TELEMETRY")

    # -------------------------------------------------
    # Speaking
    # -------------------------------------------------

    HUDIntegration.speaking()

    show_state("SPEAKING")

    # -------------------------------------------------
    # Task finished
    # -------------------------------------------------

    HUDIntegration.task_finished(
        "Developer Generator"
    )

    show_state("TASK FINISHED")

    # -------------------------------------------------
    # Notification
    # -------------------------------------------------

    HUDIntegration.notify(
        "HUD integration is working."
    )

    show_state("NOTIFICATION")

    # -------------------------------------------------
    # Idle
    # -------------------------------------------------

    HUDIntegration.idle()

    show_state("FINAL IDLE")

    print()
    print("=== HUD INTEGRATION ON TEST COMPLETE ===")
    print()


if __name__ == "__main__":
    main()