"""
JARVIS PRO
Offline Piper TTS

Completely isolated offline TTS engine.

DO NOT import:
    voice.manager
    voice.online_edge
    voice.player
"""

import re
import subprocess
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from voice.offline.offline_player import play


# =========================================================
# Configuration
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PIPER_MODEL = (
    BASE_DIR
    / "models"
    / "en_US-lessac-medium.onnx"
)

PIPER_WORKERS = 2


# =========================================================
# Piper Check
# =========================================================

def piper_available():

    try:

        result = subprocess.run(
            [
                "python",
                "-m",
                "piper",
                "--help",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )

        return result.returncode == 0

    except Exception:

        return False


# =========================================================
# Model Check
# =========================================================

def model_available():

    return (
        PIPER_MODEL.exists()
        and PIPER_MODEL.is_file()
    )


# =========================================================
# Prepare One Sentence
# =========================================================

def generate(text):

    if not text:
        return None

    text = str(text).strip()

    if not text:
        return None

    if not model_available():

        print(
            "[OFFLINE TTS] Model not found:",
            PIPER_MODEL
        )

        return None

    try:

        temp = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )

        temp.close()

        wav_file = Path(temp.name)

        print(
            "[OFFLINE TTS] Preparing:",
            wav_file.name
        )

        process = subprocess.run(

            [
                "python",
                "-m",
                "piper",

                "--model",
                str(PIPER_MODEL),

                "--output_file",
                str(wav_file),
            ],

            input=text,

            text=True,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            timeout=60,
        )

        if process.returncode != 0:

            print(
                "[OFFLINE TTS] Piper failed."
            )

            if process.stderr:

                print(
                    process.stderr.strip()
                )

            wav_file.unlink(
                missing_ok=True
            )

            return None

        if not wav_file.exists():

            return None

        if wav_file.stat().st_size == 0:

            wav_file.unlink(
                missing_ok=True
            )

            return None

        return wav_file

    except Exception as e:

        print(
            "[OFFLINE TTS ERROR]",
            e
        )

        return None


# =========================================================
# Split Text
# =========================================================

def split_sentences(text):

    if not text:
        return []

    text = str(text).strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# =========================================================
# Prepare Multiple Sentences
# =========================================================

def prepare(text):

    sentences = split_sentences(text)

    if not sentences:
        return []

    prepared = [None] * len(sentences)

    print(
        f"[OFFLINE TTS] Preparing "
        f"{len(sentences)} sentences..."
    )

    with ThreadPoolExecutor(
        max_workers=PIPER_WORKERS
    ) as executor:

        futures = {
            executor.submit(
                generate,
                sentence
            ): index

            for index, sentence
            in enumerate(sentences)
        }

        for future in as_completed(futures):

            index = futures[future]

            try:

                prepared[index] = future.result()

            except Exception as e:

                print(
                    "[OFFLINE TTS] "
                    f"Preparation error {index}:",
                    e
                )

    return prepared


# =========================================================
# Play Prepared Sentences
# =========================================================

def play_prepared(prepared):

    if not prepared:
        return False

    success = True

    for index, wav_file in enumerate(prepared):

        if not wav_file:

            success = False

            continue

        try:

            print(
                f"[OFFLINE TTS] "
                f"Playing sentence {index}"
            )

            result = play(
                wav_file
            )

            if not result:

                success = False

        except Exception as e:

            print(
                "[OFFLINE TTS] "
                f"Playback error {index}:",
                e
            )

            success = False

        finally:

            try:

                wav_file.unlink(
                    missing_ok=True
                )

                print(
                    "[OFFLINE TTS] Deleted:",
                    wav_file.name
                )

            except Exception as e:

                print(
                    "[OFFLINE TTS] "
                    "Cleanup error:",
                    e
                )

    return success


# =========================================================
# Speak Full Response
# =========================================================

def speak(text):

    prepared = prepare(text)

    if not prepared:

        return False

    return play_prepared(
        prepared
    )