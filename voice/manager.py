import threading
import requests

from core.live_execution import is_live_execution

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

from hud.integration import HUDIntegration


ONLINE = False

VOICE_THREAD = None

# =========================================================
# REMOTE SPEECH LISTENERS
# =========================================================

_SPEECH_LISTENERS = []

_SPEECH_LISTENER_LOCK = threading.Lock()


def add_speech_listener(listener):
    """
    Register a callback that receives every JARVIS
    speech message.

    The callback must accept one argument:

        listener(text)
    """

    if not callable(listener):
        return

    with _SPEECH_LISTENER_LOCK:

        if listener not in _SPEECH_LISTENERS:
            _SPEECH_LISTENERS.append(
                listener
            )


def remove_speech_listener(listener):

    with _SPEECH_LISTENER_LOCK:

        if listener in _SPEECH_LISTENERS:
            _SPEECH_LISTENERS.remove(
                listener
            )


def _notify_speech_listeners(text):

    if not text:
        return

    with _SPEECH_LISTENER_LOCK:

        listeners = list(
            _SPEECH_LISTENERS
        )

    for listener in listeners:

        try:

            listener(text)

        except Exception as exc:

            print(
                "[VOICE] Speech listener error:",
                exc
            )

def notify_speech_output(text):
    """
    Send speech text to registered remote/dashboard
    listeners without triggering TTS.
    """

    _notify_speech_listeners(
        str(text)
    )

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

        HUDIntegration.idle()

        return False

    success = False

    # -----------------------------------------------------
    # Online Edge TTS
    # -----------------------------------------------------

    if ONLINE:

        try:

            success = speak_online(
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

    if not success and not is_cancelled(session):

        try:

            success = speak_offline(text)

        except Exception as e:

            print(
                "[VOICE] Offline TTS failed:",
                e
            )

    # -----------------------------------------------------
    # HUD — Speech finished
    # -----------------------------------------------------

    HUDIntegration.idle()

    return bool(success)

# =========================================================
# PRO TTS PREPARE
# =========================================================

def prepare_speech(
    text,
    session,
):

    if not text:
        return None

    # -----------------------------------------------------
    # LIVE CONVERSATION SPEECH GATE
    # -----------------------------------------------------

    if is_live_execution():

        print(
            "[VOICE] Live execution active - "
            "suppressing speech preparation."
        )

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
    if is_live_execution():

        print(
            "[VOICE] Live execution active - "
            "suppressing prepared TTS playback."
        )

        return False

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
    notify_remote=True,
):

    global VOICE_THREAD

    if not text:

        return
    
    # -----------------------------------------------------
    # Notify connected Remote Dashboard
    #
    # This sends the same text that JARVIS is about to
    # speak to the remote chat.
    # -----------------------------------------------------

    if notify_remote:

        _notify_speech_listeners(
            str(text)
        )
    
    # -----------------------------------------------------
    # LIVE CONVERSATION SPEECH GATE
    #
    # Gemini Live is already the active speaker.
    # Prevent normal Edge/Piper TTS from speaking at the
    # same time when a skill executes through Live mode.
    # -----------------------------------------------------

    if is_live_execution():

        print(
            "[VOICE] Live execution active - "
            "suppressing normal TTS."
        )

        return

    # -----------------------------------------------------
    # Resolve speech session
    # -----------------------------------------------------

    if session is None:

        session = current_session()

    # -----------------------------------------------------
    # Current session may already be cancelled/invalid.
    #
    # This can happen when:
    #
    # old AI response
    #       ↓
    # user gives new command
    #       ↓
    # stop_speaking()
    #       ↓
    # old session cancelled
    #       ↓
    # new command wants to speak
    #
    # Create a fresh session for the new independent speech.
    # -----------------------------------------------------

    if (
        session is None
        or is_cancelled(session)
        or not is_current(session)
    ):

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
    # HUD — JARVIS is speaking
    # -----------------------------------------------------

    HUDIntegration.speaking()

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