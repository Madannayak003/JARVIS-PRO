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

import threading
from queue import Queue
import speech_recognition as sr

COMMAND_QUEUE = Queue()

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

recognizer.pause_threshold = 1.5
recognizer.phrase_threshold = 0.5
recognizer.non_speaking_duration = 0.8

_pending_text = None
_timer = None
_lock = threading.Lock()


def _dispatch():

    global _pending_text

    with _lock:

        if _pending_text:

            print("You :", _pending_text)

            COMMAND_QUEUE.put(_pending_text.lower())

            _pending_text = None


def _callback(recognizer, audio):

    global _pending_text
    global _timer

    try:

        text = recognizer.recognize_google(audio).strip()

        if not text:
            return

        with _lock:

            _pending_text = text

            if _timer:

                _timer.cancel()

            _timer = threading.Timer(

                0.4,

                _dispatch

            )

            _timer.daemon = True

            _timer.start()

    except Exception:

        pass


def start_listener():

    mic = sr.Microphone()

    with mic as source:

        recognizer.adjust_for_ambient_noise(

            source,

            duration=1

        )

    recognizer.listen_in_background(

        mic,

        _callback,

        phrase_time_limit=30

    )

    print("[MIC] Background listener started")


def get_command():

    if COMMAND_QUEUE.empty():

        return None

    return COMMAND_QUEUE.get()