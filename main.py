from skills.loader import load_all
from ai.memory import init_memory
from core.services import start_all

from voice.mode import get_mode

from hud.integration import HUDIntegration

def main():

    mode = get_mode()

    print(f"[MAIN] Voice mode: {mode}")

    # =====================================================
    # HUD — Report current voice mode
    # =====================================================

    HUDIntegration.voice_mode(
        mode
    )
    
    print(
        "[MAIN HUD] Voice mode sent to HUD:",
        mode
    )

    # =====================================================
    # OFFLINE MODE
    # =====================================================

    if mode == "offline":

        print(
            "[MAIN] Starting isolated offline JARVIS..."
        )

        from voice.offline.offline_runner import run

        return run()

    # =====================================================
    # ONLINE MODE
    # =====================================================

    print(
        "[MAIN] Starting existing online JARVIS..."
    )

    load_all()

    init_memory()

    start_all()

    from voice.online_runner import run

    return run()


if __name__ == "__main__":
    main()