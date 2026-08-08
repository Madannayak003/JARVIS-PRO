import threading
import requests

from voice.online_edge import speak_online
from voice.offline_piper import speak_offline


ONLINE = False

VOICE_STOP = threading.Event()


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
    # Online Edge-TTS
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
    # Offline Piper fallback
    # -----------------------------------------------------

    try:

        speak_offline(text)

    except Exception as e:

        print(
            "[VOICE] Offline TTS failed:",
            e
        )


# =========================================================
# Voice Thread
# =========================================================

VOICE_THREAD = None


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

    VOICE_STOP.clear()

    print(
        f"[VOICE] {text}"
    )

    # -----------------------------------------------------
    # Wait for previous speech
    # -----------------------------------------------------

    if (
        VOICE_THREAD
        and VOICE_THREAD.is_alive()
    ):

        VOICE_THREAD.join()

    # -----------------------------------------------------
    # Start voice worker
    # -----------------------------------------------------

    VOICE_THREAD = threading.Thread(
        target=_worker,
        args=(text,),
        daemon=True,
    )

    VOICE_THREAD.start()

    # -----------------------------------------------------
    # Optional synchronous wait
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

    VOICE_STOP.set()