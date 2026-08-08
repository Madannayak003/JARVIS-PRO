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

    STOP_EVENT.clear()

    with _lock:

        # -------------------------------------------------
        # Stop previous playback
        # -------------------------------------------------

        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.unload()
        except Exception:
            pass

        # -------------------------------------------------
        # Load new file
        # -------------------------------------------------

        pygame.mixer.music.load(file)

        pygame.mixer.music.play()

        # -------------------------------------------------
        # Wait for playback
        # -------------------------------------------------

        while pygame.mixer.music.get_busy():

            if STOP_EVENT.is_set():

                pygame.mixer.music.stop()

                try:
                    pygame.mixer.music.unload()
                except Exception:
                    pass

                return

            time.sleep(0.05)

        # -------------------------------------------------
        # IMPORTANT:
        # Release MP3 after playback finishes
        # -------------------------------------------------

        pygame.mixer.music.stop()

        try:

            pygame.mixer.music.unload()

        except Exception as e:

            print(
                f"[PLAYER] Could not unload audio: {e}"
            )

        # -------------------------------------------------
        # Small Windows release delay
        # -------------------------------------------------

        time.sleep(0.1)


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