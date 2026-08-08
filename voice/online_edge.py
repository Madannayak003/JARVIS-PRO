import asyncio
import threading
import time
import edge_tts

from pathlib import Path
from uuid import uuid4

from voice.state import STOP_EVENT
from voice.player import play


CACHE = Path(__file__).parent / "cache"
CACHE.mkdir(exist_ok=True)

VOICE = "en-US-GuyNeural"


# =========================================================
# Generate Speech
# =========================================================

async def _generate(text, outfile):

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
    )

    await communicate.save(outfile)


# =========================================================
# Worker
# =========================================================

def _worker(text):

    outfile = CACHE / f"{uuid4().hex}.mp3"

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:

        # -------------------------------------------------
        # Generate MP3
        # -------------------------------------------------

        loop.run_until_complete(
            _generate(
                text,
                str(outfile),
            )
        )

    except Exception as e:

        print(
            f"[EDGE TTS ERROR] {e}"
        )

        return False

    finally:

        try:
            loop.close()

        except Exception:
            pass

    # -----------------------------------------------------
    # Stop check
    # -----------------------------------------------------

    if STOP_EVENT.is_set():

        _cleanup_file(outfile)

        return False

    # -----------------------------------------------------
    # Play
    #
    # IMPORTANT:
    # Do NOT delete immediately after play().
    # Windows may still have the MP3 open.
    # -----------------------------------------------------

    try:

        play(str(outfile))

    except Exception as e:

        print(
            f"[EDGE TTS PLAY ERROR] {e}"
        )

        _cleanup_file(outfile)

        return False

    # -----------------------------------------------------
    # Cleanup after playback
    # -----------------------------------------------------

    _cleanup_file_later(outfile)

    return True


# =========================================================
# File Cleanup
# =========================================================

def _cleanup_file(path, attempts=5):

    for _ in range(attempts):

        try:

            if path.exists():

                path.unlink()

            return True

        except PermissionError:

            time.sleep(0.3)

        except Exception as e:

            print(
                f"[EDGE TTS CACHE] {e}"
            )

            return False

    print(
        f"[EDGE TTS CACHE] Could not remove: {path.name}"
    )

    return False


def _cleanup_file_later(path):

    def cleanup():

        # Give Windows audio player time to release file.
        time.sleep(1)

        _cleanup_file(path)

    threading.Thread(
        target=cleanup,
        daemon=True,
    ).start()


# =========================================================
# Public API
# =========================================================

def speak_online(text, wait=False):

    if not text:

        return False

    thread = threading.Thread(
        target=_worker,
        args=(text,),
        daemon=True,
    )

    thread.start()

    if wait:

        thread.join()

    return True