# import threading
# from queue import Queue
# import speech_recognition as sr

# COMMAND_QUEUE = Queue()

# recognizer = sr.Recognizer()

# recognizer.energy_threshold = 300
# recognizer.dynamic_energy_threshold = True

# # Wait longer before deciding speech has ended
# recognizer.pause_threshold = 2.0

# # Ignore tiny sounds
# recognizer.phrase_threshold = 0.5

# # Keep recording through short pauses
# recognizer.non_speaking_duration = 1.0

# def _callback(recognizer, audio):

#     try:

#         text = recognizer.recognize_google(audio)

#         print("You :", text)

#         COMMAND_QUEUE.put(text.lower())

#     except Exception:
#         pass

# def start_listener():

#     mic = sr.Microphone()

#     with mic as source:

#         recognizer.adjust_for_ambient_noise(source, duration=1)

#     recognizer.listen_in_background(
#         mic,
#         _callback,
#         phrase_time_limit=30
#     )

#     print("[MIC] Background listener started")


# def get_command():

#     if COMMAND_QUEUE.empty():
#         return None

#     return COMMAND_QUEUE.get()

# ======================================================================================

# import threading
# from queue import Queue
# import speech_recognition as sr

# COMMAND_QUEUE = Queue()

# recognizer = sr.Recognizer()

# recognizer.energy_threshold = 300
# recognizer.dynamic_energy_threshold = True

# recognizer.pause_threshold = 1.5
# recognizer.phrase_threshold = 0.5
# recognizer.non_speaking_duration = 0.8

# _pending_text = None
# _timer = None
# _lock = threading.Lock()


# def _dispatch():

#     global _pending_text

#     with _lock:

#         if _pending_text:

#             print("You :", _pending_text)

#             COMMAND_QUEUE.put(_pending_text.lower())

#             _pending_text = None


# def _callback(recognizer, audio):

#     global _pending_text
#     global _timer

#     try:

#         text = recognizer.recognize_google(audio).strip()

#         if not text:
#             return

#         with _lock:

#             _pending_text = text

#             if _timer:

#                 _timer.cancel()

#             _timer = threading.Timer(

#                 0.4,

#                 _dispatch

#             )

#             _timer.daemon = True

#             _timer.start()

#     except Exception:

#         pass


# def start_listener():

#     mic = sr.Microphone()

#     with mic as source:

#         recognizer.adjust_for_ambient_noise(

#             source,

#             duration=1

#         )

#     recognizer.listen_in_background(

#         mic,

#         _callback,

#         phrase_time_limit=30

#     )

#     print("[MIC] Background listener started")


# def get_command():

#     if COMMAND_QUEUE.empty():

#         return None

#     return COMMAND_QUEUE.get()

#  =====================================================================================

import threading
from queue import Queue
import speech_recognition as sr


# ============================================================
# COMMAND QUEUE
# ============================================================

COMMAND_QUEUE = Queue()


# ============================================================
# SPEECH RECOGNIZER
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

recognizer.pause_threshold = 1.5
recognizer.phrase_threshold = 0.5
recognizer.non_speaking_duration = 0.8


# ============================================================
# INTERNAL STATE
# ============================================================

_pending_text = None
_timer = None

_lock = threading.Lock()

_listener_stop = None

_listener_running = False

_listener_paused = False


# ============================================================
# DISPATCH RECOGNIZED TEXT
# ============================================================

def _dispatch():

    global _pending_text

    with _lock:

        if _pending_text:

            # Do not dispatch normal speech while
            # Live Conversation owns the microphone.

            if _listener_paused:

                _pending_text = None

                return

            print(
                "You :",
                _pending_text
            )

            COMMAND_QUEUE.put(
                _pending_text.lower()
            )

            _pending_text = None


# ============================================================
# GOOGLE SPEECH CALLBACK
# ============================================================

def _callback(
    recognizer,
    audio,
):

    global _pending_text
    global _timer

    # --------------------------------------------------------
    # Ignore normal listener while Live Conversation is active
    # --------------------------------------------------------

    with _lock:

        if _listener_paused:

            return

    try:

        text = (
            recognizer
            .recognize_google(
                audio
            )
            .strip()
        )

        if not text:

            return

        with _lock:

            # Live Conversation may have started while
            # Google recognition was processing.

            if _listener_paused:

                return

            _pending_text = text

            if _timer:

                _timer.cancel()

            _timer = threading.Timer(
                0.4,
                _dispatch,
            )

            _timer.daemon = True

            _timer.start()

    except Exception:

        pass


# ============================================================
# START LISTENER
# ============================================================

def start_listener():

    global _listener_stop
    global _listener_running
    global _listener_paused

    with _lock:

        # Already running.

        if _listener_running:

            _listener_paused = False

            print(
                "[MIC] Background listener already running"
            )

            return

    mic = sr.Microphone()

    with mic as source:

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1,
        )

    _listener_stop = (
        recognizer.listen_in_background(
            mic,
            _callback,
            phrase_time_limit=30,
        )
    )

    with _lock:

        _listener_running = True

        _listener_paused = False

    print(
        "[MIC] Background listener started"
    )


# ============================================================
# PAUSE LISTENER
# ============================================================

def pause_listener():

    global _listener_paused
    global _pending_text
    global _timer

    with _lock:

        _listener_paused = True

        _pending_text = None

        if _timer:

            _timer.cancel()

            _timer = None

    print(
        "[MIC] Background listener paused"
    )


# ============================================================
# RESUME LISTENER
# ============================================================

def resume_listener():

    global _listener_paused

    with _lock:

        if not _listener_running:

            print(
                "[MIC] Cannot resume: "
                "listener is not running"
            )

            return False

        _listener_paused = False

    print(
        "[MIC] Background listener resumed"
    )

    return True


# ============================================================
# STOP LISTENER
# ============================================================

def stop_listener():

    global _listener_stop
    global _listener_running
    global _listener_paused
    global _pending_text
    global _timer

    with _lock:

        _listener_paused = True

        _pending_text = None

        if _timer:

            _timer.cancel()

            _timer = None

        stop_function = _listener_stop

        _listener_stop = None

        _listener_running = False

    if stop_function:

        try:

            stop_function(
                wait_for_stop=False
            )

        except Exception:

            try:

                stop_function()

            except Exception:

                pass

    print(
        "[MIC] Background listener stopped"
    )


# ============================================================
# LISTENER STATUS
# ============================================================

def listener_running():

    with _lock:

        return _listener_running


def listener_paused():

    with _lock:

        return _listener_paused


# ============================================================
# COMMAND
# ============================================================

def get_command():

    if COMMAND_QUEUE.empty():

        return None

    return COMMAND_QUEUE.get()