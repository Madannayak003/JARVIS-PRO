import asyncio
import threading
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
        # Generate
        # -------------------------------------------------

        print(
            f"[EDGE TTS] Generating: {outfile.name}"
        )

        loop.run_until_complete(
            _generate(
                text,
                str(outfile),
            )
        )

        # -------------------------------------------------
        # Stop requested
        # -------------------------------------------------

        if STOP_EVENT.is_set():

            print(
                "[EDGE TTS] Playback cancelled"
            )

            return False

        # -------------------------------------------------
        # Play
        # -------------------------------------------------

        result = play(
            str(outfile)
        )

        return result

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

        # -------------------------------------------------
        # IMPORTANT:
        #
        # DO NOT DELETE MP3.
        #
        # Files remain in voice/cache/
        # -------------------------------------------------


# =========================================================
# Public API
# =========================================================

def speak_online(
    text,
    wait=False,
):

    if not text:
        return False

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # When wait=True, run directly.
    #
    # This avoids creating:
    #
    # manager thread
    #       ↓
    # edge thread
    #       ↓
    # asyncio
    #
    # unnecessarily.
    # -----------------------------------------------------

    if wait:

        return _worker(text)

    # -----------------------------------------------------
    # Asynchronous mode
    # -----------------------------------------------------

    thread = threading.Thread(
        target=_worker,
        args=(text,),
        daemon=True,
        name="EdgeTTS",
    )

    thread.start()

    return True