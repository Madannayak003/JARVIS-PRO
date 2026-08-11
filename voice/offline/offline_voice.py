"""
JARVIS PRO
Completely Isolated Offline Voice Mode

STT  -> Faster-Whisper
AI   -> Ollama
TTS  -> Piper

This module does NOT import or use:
- voice.manager
- voice.online_edge
- core.listener
- online STT
- Edge TTS
"""

import time

from voice.offline.offline_stt import (
    calibrate,
    listen_once,
)

from voice.offline.offline_tts import (
    speak,
)

# =========================================================
# Ollama
# =========================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

OLLAMA_MODEL = "jarvis"


def ask_ollama(prompt):
    """
    Completely local Ollama request.
    """

    import requests

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            ""
        ).strip()

    except Exception as e:

        print(
            "[OFFLINE AI ERROR]",
            e
        )

        return None


# =========================================================
# Offline Voice Mode
# =========================================================

def run():

    print()
    print("=" * 42)
    print("       JARVIS OFFLINE VOICE MODE")
    print("=" * 42)
    print("[OFFLINE VOICE] STT  : Faster-Whisper")
    print("[OFFLINE VOICE] AI   : Ollama")
    print("[OFFLINE VOICE] TTS  : Piper")
    print("[OFFLINE VOICE] NET  : Not required")
    print("=" * 42)
    print()

    # -----------------------------------------------------
    # Calibrate microphone ONLY ONCE
    # -----------------------------------------------------

    mic = calibrate()

    print()
    print(
        "[OFFLINE VOICE] Ready."
    )
    print(
        "[OFFLINE VOICE] Speak a command."
    )
    print(
        "[OFFLINE VOICE] Press Ctrl+C to exit."
    )
    print()

    # =====================================================
    # Continuous Offline Loop
    # =====================================================

    while True:

        try:

            # -------------------------------------------------
            # Listen
            # -------------------------------------------------

            text = listen_once(
                mic,
                timeout=3,
                phrase_time_limit=8,
            )

            # -------------------------------------------------
            # Nothing recognized
            # -------------------------------------------------

            if not text:

                continue

            text = text.strip()

            if not text:

                continue

            print()
            print(
                "[OFFLINE VOICE] You:",
                text
            )

            # -------------------------------------------------
            # Exit commands
            # -------------------------------------------------

            command = text.lower().strip()

            if command in [
                "exit",
                "quit",
                "stop offline mode",
                "shutdown offline mode",
            ]:

                print(
                    "[OFFLINE VOICE] Shutting down."
                )

                break

            # -------------------------------------------------
            # Local AI
            # -------------------------------------------------

            print(
                "[OFFLINE AI] Thinking..."
            )

            response = ask_ollama(
                text
            )

            if not response:

                print(
                    "[OFFLINE AI] "
                    "No response."
                )

                continue

            # -------------------------------------------------
            # Print response
            # -------------------------------------------------

            print(
                "[OFFLINE AI] Response:",
                response
            )

            # -------------------------------------------------
            # Piper
            # -------------------------------------------------

            speak(
                response
            )

            # -------------------------------------------------
            # Small protection against immediately
            # capturing residual audio.
            # -------------------------------------------------

            time.sleep(0.15)

        except KeyboardInterrupt:

            print()
            print(
                "[OFFLINE VOICE] Stopped."
            )

            break

        except Exception as e:

            print(
                "[OFFLINE VOICE ERROR]",
                e
            )

            time.sleep(0.2)


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":

    run()