"""
JARVIS PRO
Offline Voice Runner

Completely isolated offline voice runtime.

Uses ONLY:
offline_stt
offline_ai
offline_tts

DO NOT import:
voice.manager
voice.online_edge
core.listener
core.assistant
"""

from voice.offline.offline_stt import (
    calibrate,
    listen_once,
)

from voice.offline.offline_ai import (
    get_ai,
)

from voice.offline.offline_tts import (
    speak,
)

from hud.adapter import HUDAdapter
from voice.mode import get_mode


def run():

    print()
    print("==========================================")
    print("       JARVIS OFFLINE VOICE MODE")
    print("==========================================")
    print("[OFFLINE VOICE] STT  : Faster-Whisper")
    print("[OFFLINE VOICE] AI   : Ollama")
    print("[OFFLINE VOICE] TTS  : Piper")
    print("[OFFLINE VOICE] NET  : Not required")
    print("==========================================")
    print()

    # -----------------------------------------
    # Initialize offline AI
    # -----------------------------------------

    print("[OFFLINE VOICE] Initializing AI...")

    ai = get_ai()

    # -----------------------------------------
    # Initialize HUD
    # -----------------------------------------

    HUDAdapter.voice_mode(
        get_mode()
    )

    HUDAdapter.idle()

    # -----------------------------------------
    # Calibrate microphone
    # -----------------------------------------

    print(
        "[OFFLINE VOICE] Preparing microphone..."
    )

    mic = calibrate()

    print()
    print("[OFFLINE VOICE] Ready.")
    print("[OFFLINE VOICE] Speak a command.")
    print("[OFFLINE VOICE] Press Ctrl+C to exit.")
    print()

    # -----------------------------------------
    # Offline conversation loop
    # -----------------------------------------

    try:

        while True:

            # =================================
            # LISTENING
            # =================================

            HUDAdapter.listening()

            text = listen_once(
                mic,
                timeout=None,
                phrase_time_limit=10,
            )

            # ---------------------------------
            # No speech recognized
            # ---------------------------------

            if not text:

                HUDAdapter.idle()

                continue

            print()
            print(
                "[OFFLINE VOICE] You:",
                text
            )

            # =================================
            # THINKING
            # =================================

            print(
                "[OFFLINE AI] Thinking..."
            )

            HUDAdapter.thinking()

            response = ai.ask(
                text
            )

            # ---------------------------------
            # AI failed / no response
            # ---------------------------------

            if not response:

                HUDAdapter.idle()

                continue

            print()
            print(
                "[OFFLINE VOICE] JARVIS:",
                response
            )

            # =================================
            # SPEAKING
            # =================================

            HUDAdapter.speaking()

            speak(
                response
            )

            # =================================
            # SPEECH FINISHED
            # =================================

            HUDAdapter.idle()

            print()

    except KeyboardInterrupt:

        # -------------------------------------
        # Always return HUD to idle
        # -------------------------------------

        HUDAdapter.idle()

        print()
        print(
            "[OFFLINE VOICE] Stopped."
        )


if __name__ == "__main__":
    run()