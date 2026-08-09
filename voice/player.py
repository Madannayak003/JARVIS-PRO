import pygame
import threading
import time

from voice.state import STOP_EVENT

pygame.mixer.init()

_lock = threading.Lock()


# =========================================================
# Play
# =========================================================

def play(file):

    with _lock:

        # -------------------------------------------------
        # If stop was requested, don't start audio
        # -------------------------------------------------

        if STOP_EVENT.is_set():
            return False

        # -------------------------------------------------
        # Stop previous playback
        # -------------------------------------------------

        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.unload()
        except Exception:
            pass

        # -------------------------------------------------
        # Load
        # -------------------------------------------------

        try:

            pygame.mixer.music.load(file)

            if STOP_EVENT.is_set():
                return False

            pygame.mixer.music.play()

        except Exception as e:

            print(
                f"[PLAYER ERROR] Could not play audio: {e}"
            )

            return False

        # -------------------------------------------------
        # Wait
        # -------------------------------------------------

        while pygame.mixer.music.get_busy():

            if STOP_EVENT.is_set():

                pygame.mixer.music.stop()

                try:
                    pygame.mixer.music.unload()
                except Exception:
                    pass

                return False

            time.sleep(0.05)

        # -------------------------------------------------
        # Release pygame resource
        # -------------------------------------------------

        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.unload()
        except Exception as e:
            print(
                f"[PLAYER] Could not unload audio: {e}"
            )

        return True


# =========================================================
# Stop
# =========================================================

def stop():

    STOP_EVENT.set()

    with _lock:

        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.unload()
        except Exception:
            pass


# =========================================================
# Speaking Status
# =========================================================

def speaking():

    return pygame.mixer.music.get_busy()