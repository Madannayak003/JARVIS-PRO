"""
=============================================================
JARVIS PRO — MAIN APPLICATION ENTRY POINT
=============================================================
"""

from skills.loader import load_all
from ai.memory import init_memory
from core.services import start_all

from voice.mode import get_mode

from hud.integration import HUDIntegration
from hud.runtime import hud_runtime
from hud.web_bridge import hud_web

from dashboard.server import DashboardServer


def main():

    mode = get_mode()

    print(
        f"[MAIN] Voice mode: {mode}"
    )

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
    
    # =====================================================
    # HUD RUNTIME
    # =====================================================

    hud_runtime.start()

    print(
        "[MAIN HUD] HUD runtime started."
    )

    # =====================================================
    # HUD WEB BRIDGE
    # =====================================================

    if hud_web.start():

        print(
            "[MAIN HUD] Web HUD bridge started."
        )

    # =====================================================
    # LIVE CONVERSATION
    # =====================================================

    from core.registry import register

    from voice.live_conversation import (
        start_live_conversation,
        stop_live_conversation,
        live_conversation_status,
    )

    register(
        "start_live_conversation",
        start_live_conversation,
        category="voice",
    )

    register(
        "stop_live_conversation",
        stop_live_conversation,
        category="voice",
    )

    register(
        "live_conversation_status",
        live_conversation_status,
        category="voice",
    )

    print(
        "[LIVE] Live Conversation actions registered."
    )

    # =====================================================
    # REMOTE DASHBOARD
    # =====================================================

    from core.dispatcher import dispatch

    remote_server = DashboardServer(
        command_handler=dispatch,
        live_stop_handler=stop_live_conversation,
    )

    remote_server.new_pairing_pin()

    if remote_server.start():

        print(
            "[REMOTE] JARVIS Dashboard:"
        )

        print(
            f"[REMOTE] {remote_server.url()}"
        )

        print(
            "[REMOTE] Pairing PIN:"
        )

        print(
            remote_server._pin
        )

        print(
            "[REMOTE] Dashboard Live stop control: READY"
        )

    # =====================================================
    # EXISTING ONLINE VOICE
    # =====================================================

    from voice.online_runner import run

    return run()


if __name__ == "__main__":

    main()