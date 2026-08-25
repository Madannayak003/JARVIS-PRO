"""
=============================================================
JARVIS PRO — MAIN APPLICATION ENTRY POINT
=============================================================

Purpose:
--------
This file is the primary entry point of JARVIS PRO.

It is responsible for initializing and starting the complete
JARVIS system based on the selected voice operating mode.

The main startup flow is:

    1. Detect the current voice mode
    2. Report the mode to the HUD
    3. If OFFLINE mode:
           → Start isolated offline JARVIS
    4. If ONLINE mode:
           → Load all skills
           → Initialize memory
           → Start core services
           → Start the online voice runner

-------------------------------------------------------------
STARTUP ARCHITECTURE
-------------------------------------------------------------

                    main()
                       │
                       ▼
                 get_mode()
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
          OFFLINE             ONLINE
              │                 │
              ▼                 ▼
      offline_runner       load_all()
                              │
                              ▼
                         init_memory()
                              │
                              ▼
                         start_all()
                              │
                              ▼
                      online_runner

-------------------------------------------------------------
VOICE MODE
-------------------------------------------------------------

The voice mode is obtained through:

    voice.mode.get_mode()

The returned mode determines which JARVIS runtime should be
started.

Supported startup paths:

    "offline"
        Starts the isolated offline JARVIS runtime.

    Other / online mode
        Starts the existing online JARVIS runtime.

-------------------------------------------------------------
HUD INTEGRATION
-------------------------------------------------------------

Before starting either runtime, the detected voice mode is
sent to the HUD through:

    HUDIntegration.voice_mode(mode)

This allows the visual HUD interface to remain synchronized
with the current JARVIS voice operating mode.

-------------------------------------------------------------
OFFLINE MODE
-------------------------------------------------------------

Offline mode intentionally starts an isolated JARVIS runtime.

It imports:

    voice.offline.offline_runner.run

Only the offline runner is started in this branch.

This keeps offline execution separated from the normal online
startup pipeline.

-------------------------------------------------------------
ONLINE MODE
-------------------------------------------------------------

The online startup path initializes the existing JARVIS
subsystems in the following order:

    load_all()
        ↓
    init_memory()
        ↓
    start_all()
        ↓
    voice.online_runner.run()

Meaning:

    load_all()
        Loads and registers all available JARVIS skills.

    init_memory()
        Initializes the JARVIS memory system before the voice
        runtime begins.

    start_all()
        Starts the required core/background services.

    voice.online_runner.run()
        Starts the main online voice interaction loop.

-------------------------------------------------------------
IMPORTANT DESIGN PRINCIPLE
-------------------------------------------------------------

This file acts as the SYSTEM BOOTSTRAPPER.

It does NOT contain the implementation of:

    - Voice recognition
    - AI reasoning
    - Planner logic
    - Skill logic
    - Memory processing
    - Core service implementation
    - HUD rendering
    - Offline voice processing
    - Online voice processing

Instead, it coordinates the correct initialization order
and delegates the actual work to the appropriate modules.

-------------------------------------------------------------
INITIALIZATION ORDER
-------------------------------------------------------------

The initialization order is intentional.

ONLINE:

    Mode Detection
        ↓
    HUD Mode Synchronization
        ↓
    Skill Loading
        ↓
    Memory Initialization
        ↓
    Core Services
        ↓
    Online Voice Runner

OFFLINE:

    Mode Detection
        ↓
    HUD Mode Synchronization
        ↓
    Offline Voice Runner

-------------------------------------------------------------
FAILURE / SAFETY BEHAVIOR
-------------------------------------------------------------

The function returns the result of the selected runner:

    offline → offline_runner.run()
    online  → online_runner.run()

The Python entry-point guard ensures that main() is executed
only when this file is launched directly.

-------------------------------------------------------------
FILE ROLE IN JARVIS PRO
-------------------------------------------------------------

This file is the top-level BOOT / ORCHESTRATION layer.

It connects:

    Voice Mode
        +
    HUD
        +
    Skills
        +
    Memory
        +
    Core Services
        +
    Voice Runtime

without directly implementing those systems.

=============================================================
"""
"""
#################################################################################################################################################
"""
from skills.loader import load_all
from ai.memory import init_memory
from core.services import start_all

from voice.mode import get_mode

from hud.integration import HUDIntegration

from services.remote_control import RemoteControlServer

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
    
    # =====================================================
    # REMOTE CONTROL
    # =====================================================

    from core.dispatcher import dispatch

    remote_server = RemoteControlServer(
        command_handler=dispatch
    )

    remote_server.new_pairing_pin()

    if remote_server.start():

        print(
            "[REMOTE] JARVIS Remote:"
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

    from voice.online_runner import run

    return run()


if __name__ == "__main__":
    main()