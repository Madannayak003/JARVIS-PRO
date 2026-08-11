import threading
import requests

from voice.online_edge import (
    speak_online,
    generate_audio,
    play_audio,
)

from voice.offline_piper import speak_offline

from voice.state import (
    create_session,
    current_session,
    cancel_current,
    is_current,
    is_cancelled,
)


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
# Start New Speech Session
# =========================================================

def start_speech_session():

    """
    Start a completely new voice response.

    Any previous response becomes permanently invalid.
    """

    # Stop old audio first.
    from voice.player import stop as stop_audio

    stop_audio()

    session = create_session()

    print(
        f"[VOICE] New speech session started: "
        f"{session.session_id}"
    )

    return session


# =========================================================
# Voice Worker
# =========================================================

def _worker(text, session):

    if not text:

        return False

    # -----------------------------------------------------
    # Never speak cancelled session
    # -----------------------------------------------------

    if is_cancelled(session):

        print(
            "[VOICE] Speech cancelled before TTS"
        )

        return False

    # -----------------------------------------------------
    # Online Edge TTS
    # -----------------------------------------------------

    if ONLINE:

        try:

            return speak_online(
                text,
                wait=True,
                session=session,
            )

        except Exception as e:

            print(
                "[VOICE] Online TTS failed:",
                e
            )

    # -----------------------------------------------------
    # Offline Piper
    # -----------------------------------------------------

    if is_cancelled(session):

        return False

    try:

        speak_offline(text)

        return True

    except Exception as e:

        print(
            "[VOICE] Offline TTS failed:",
            e
        )

        return False

# =========================================================
# PRO TTS PREPARE
# =========================================================

def prepare_speech(
    text,
    session,
):

    if not text:

        return None

    if not is_current(session):

        return None

    if is_cancelled(session):

        return None

    # -----------------------------------------------------
    # Online Edge TTS
    # -----------------------------------------------------

    if ONLINE:

        try:

            return generate_audio(
                text,
                session,
            )

        except Exception as e:

            print(
                "[VOICE] "
                "Speech preparation failed:",
                e
            )

            return None

    # -----------------------------------------------------
    # Offline mode
    #
    # Returning None tells the pipeline to use the
    # normal synchronous fallback.
    # -----------------------------------------------------

    return None


# =========================================================
# PRO TTS PLAY PREPARED AUDIO
# =========================================================

def play_prepared_speech(
    audio_file,
    session,
):

    if not audio_file:

        return False

    if not is_current(session):

        return False

    if is_cancelled(session):

        return False

    try:

        return play_audio(
            audio_file,
            session,
        )

    except Exception as e:

        print(
            "[VOICE] "
            "Prepared playback failed:",
            e
        )

        return False
    
# =========================================================
# Speak
# =========================================================

def speak(
    text,
    wait=False,
    session=None,
):

    global VOICE_THREAD

    if not text:

        return

    # -----------------------------------------------------
    # Use supplied session
    # -----------------------------------------------------

    if session is None:

        session = current_session()

    # -----------------------------------------------------
    # If no session exists, create one.
    # -----------------------------------------------------

    if session is None:

        session = start_speech_session()

    # -----------------------------------------------------
    # Old / cancelled session
    # -----------------------------------------------------

    if not is_current(session):

        print(
            "[VOICE] Speech rejected: "
            f"old session {session.session_id}"
        )

        return

    print(
        f"[VOICE] {text}"
    )

    # -----------------------------------------------------
    # Synchronous mode
    #
    # Used by AI speech queue.
    # -----------------------------------------------------

    if wait:

        _worker(
            text,
            session
        )

        return

    # -----------------------------------------------------
    # Async mode
    # -----------------------------------------------------

    VOICE_THREAD = threading.Thread(

        target=_worker,

        args=(
            text,
            session,
        ),

        daemon=True,

        name="JARVIS-VoiceWorker",

    )

    VOICE_THREAD.start()


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

    # Cancel current response.
    cancel_current()

    # Stop actual audio.
    stop_audio()