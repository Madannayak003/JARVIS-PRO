import threading
import requests

from voice.online_edge import speak_online
from voice.offline_piper import speak_offline
from voice.state import STOP_EVENT


ONLINE = False

VOICE_THREAD = None


# =========================================================
# Internet Detection
# =========================================================

def check_internet():

    global ONLINE

    try:

        requests.get(
            "https://www.google.com",
            timeout=2
        )

        ONLINE = True

    except Exception:

        ONLINE = False


check_internet()


# =========================================================
# Voice Worker
# =========================================================

def _worker(text):

    # -----------------------------------------------------
    # Online Edge TTS
    # -----------------------------------------------------

    if ONLINE:

        try:

            speak_online(
                text,
                wait=True
            )

            return

        except Exception as e:

            print(
                "[VOICE] Online TTS failed:",
                e
            )

    # -----------------------------------------------------
    # Offline Piper
    # -----------------------------------------------------

    try:

        speak_offline(text)

    except Exception as e:

        print(
            "[VOICE] Offline TTS failed:",
            e
        )


# =========================================================
# Speak
# =========================================================

def speak(
    text,
    wait=False,
):

    global VOICE_THREAD

    if not text:
        return

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # If the previous conversation was stopped,
    # allow the next voice request to speak again.
    # -----------------------------------------------------

    if STOP_EVENT.is_set():

        print(
            "[VOICE] Resetting stop state for new speech"
        )

        STOP_EVENT.clear()

    print(
        f"[VOICE] {text}"
    )

    # -----------------------------------------------------
    # Start immediately
    #
    # DO NOT wait for previous voice thread here.
    #
    # This is important for streaming AI responses.
    # -----------------------------------------------------

    VOICE_THREAD = threading.Thread(
        target=_worker,
        args=(text,),
        daemon=True,
    )

    VOICE_THREAD.start()

    # -----------------------------------------------------
    # Optional synchronous mode
    # -----------------------------------------------------

    if wait:

        VOICE_THREAD.join()


# =========================================================
# Wait For Speech
# =========================================================

def wait_for_speech():

    global VOICE_THREAD

    if (
        VOICE_THREAD
        and VOICE_THREAD.is_alive()
    ):

        VOICE_THREAD.join()


# =========================================================
# Stop Speaking
# =========================================================

def stop_speaking():

    from voice.player import stop as stop_audio

    print(
        "[VOICE] Stopping speech"
    )

    STOP_EVENT.set()

    stop_audio()