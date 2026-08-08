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
# Cleanup MP3
# =========================================================

def _cleanup_file(outfile):

    if not outfile.exists():
        return

    # Windows may keep the file locked briefly after playback.
    # Retry several times instead of treating this as an error.

    for attempt in range(10):

        try:

            outfile.unlink()

            print(
                f"[EDGE TTS CACHE] Removed: {outfile.name}"
            )

            return

        except PermissionError:

            if attempt < 9:

                time.sleep(0.5)

            else:

                print(
                    "[EDGE TTS CACHE] "
                    f"Could not remove after retries: "
                    f"{outfile.name}"
                )

        except Exception as e:

            print(
                f"[EDGE TTS CACHE] Cleanup error: {e}"
            )

            return


# =========================================================
# Worker
# =========================================================

def _worker(text):

    outfile = CACHE / f"{uuid4().hex}.mp3"

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:

        # -------------------------------------------------
        # Generate
        # -------------------------------------------------

        loop.run_until_complete(
            _generate(
                text,
                str(outfile),
            )
        )

        # -------------------------------------------------
        # Stop requested before playback
        # -------------------------------------------------

        if STOP_EVENT.is_set():

            return False

        # -------------------------------------------------
        # Play
        # -------------------------------------------------

        play(str(outfile))

        return True

    except Exception as e:

        print(
            f"[EDGE TTS ERROR] {e}"
        )

        return False

    finally:

        # -------------------------------------------------
        # Close asyncio loop
        # -------------------------------------------------

        try:

            loop.close()

        except Exception:
            pass

        # -------------------------------------------------
        # Give audio backend a moment to release file
        # -------------------------------------------------

        time.sleep(0.2)

        # -------------------------------------------------
        # Remove temporary MP3
        # -------------------------------------------------

        _cleanup_file(outfile)


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

    # -----------------------------------------------------
    # Synchronous mode
    # -----------------------------------------------------

    if wait:

        thread.join()

        return True

    return True