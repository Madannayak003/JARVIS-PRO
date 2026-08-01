import pygame
import threading
from voice.state import STOP_EVENT
import time

pygame.mixer.init()

_lock = threading.Lock()


def play(file):

    STOP_EVENT.clear()

    with _lock:

        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.unload()
        except:
            pass

        pygame.mixer.music.load(file)

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():

            if STOP_EVENT.is_set():

                pygame.mixer.music.stop()
                return

            time.sleep(0.05)


def stop():

    STOP_EVENT.set()

    pygame.mixer.music.stop()

    try:
        pygame.mixer.music.unload()
    except:
        pass


def speaking():

    return pygame.mixer.music.get_busy()