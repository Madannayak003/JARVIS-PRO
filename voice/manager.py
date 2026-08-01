import threading
import requests

from voice.online_edge import speak_online
from voice.offline_piper import speak_offline

ONLINE = False

VOICE_STOP = threading.Event()

def check_internet():

    global ONLINE

    try:

        requests.get(
            "https://www.google.com",
            timeout=2
        )

        ONLINE = True

    except:

        ONLINE = False

check_internet()

def _worker(text):

    if ONLINE:

        try:

            speak_online(text)
            return

        except Exception as e:

            print("[VOICE]", e)

    speak_offline(text)

VOICE_THREAD = None


def speak(text):

    global VOICE_THREAD

    if not text:
        return

    VOICE_STOP.clear()

    print(f"[VOICE] {text}")

    # Wait for previous speech to finish
    if VOICE_THREAD and VOICE_THREAD.is_alive():

        VOICE_THREAD.join()

    VOICE_THREAD = threading.Thread(

        target=_worker,

        args=(text,),

        daemon=True

    )

    VOICE_THREAD.start()
    
def stop_speaking():

    VOICE_STOP.set()