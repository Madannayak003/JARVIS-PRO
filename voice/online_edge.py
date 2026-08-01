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


async def _generate(text, outfile):

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE
    )

    await communicate.save(outfile)


def _worker(text):
    
    STOP_EVENT.clear()      # <-- ADD THIS


    outfile = CACHE / f"{uuid4().hex}.mp3"

    # Create a NEW event loop for this thread
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:

        loop.run_until_complete(
            _generate(text, str(outfile))
        )

    finally:

        loop.close()

    if STOP_EVENT.is_set():
        return

    play(str(outfile))


def speak_online(text):

    STOP_EVENT.clear()      # <-- ADD THIS

    thread = threading.Thread(
        target=_worker,
        args=(text,),
        daemon=True
    )

    thread.start()