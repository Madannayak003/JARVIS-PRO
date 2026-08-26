"""
JARVIS PRO - Natural Live Conversation

Gemini Native Audio live conversation mode.

Live Conversation is an OPTIONAL exclusive voice mode.

NORMAL MODE:
    core.listener
        ↓
    normal JARVIS
        ↓
    Edge TTS

LIVE MODE:
    Gemini Native Audio
        ↓
    sounddevice microphone
        ↓
    Gemini audio output

When Live Conversation starts, the normal JARVIS
listener is paused.

When Live Conversation stops, the normal JARVIS
listener is resumed.

Live Conversation can be stopped by:
- voice phrase: "stop live conversation"
- voice phrase: "stop live mode"
- Remote Control stop button
- normal program shutdown
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
from pathlib import Path

import sounddevice as sd

from core.listener import (
    pause_listener,
    resume_listener,
)

try:
    from google import genai
    from google.genai import types

except ImportError as exc:

    raise RuntimeError(
        "Install google-genai before using Live Conversation: "
        "pip install google-genai"
    ) from exc


# ============================================================
# CONFIGURATION
# ============================================================

LIVE_MODEL = os.getenv(
    "JARVIS_LIVE_MODEL",
    "models/gemini-2.5-flash-native-audio-preview-12-2025",
)

INPUT_RATE = 16000

OUTPUT_RATE = 24000

CHANNELS = 1

BLOCK_SIZE = 1024


# ============================================================
# STOP PHRASES
# ============================================================

_STOP_PHRASES = (
    "stop live conversation",
    "stop live mode",
    "exit live conversation",
    "exit live mode",
    "end live conversation",
    "end live mode",
    "leave live conversation",
    "leave live mode",
    "go back to normal mode",
)


# ============================================================
# API KEY
# ============================================================

def _api_key() -> str:

    key = os.getenv(
        "GEMINI_API_KEY",
        "",
    ).strip()

    if key:

        return key

    config_path = (
        Path(__file__).resolve().parents[1]
        / "config"
        / "api_keys.json"
    )

    try:

        data = json.loads(
            config_path.read_text(
                encoding="utf-8"
            )
        )

        return str(
            data.get(
                "gemini_api_key",
                "",
            )
        ).strip()

    except Exception:

        return ""


# ============================================================
# SYSTEM PROMPT
# ============================================================

def _system_prompt() -> str:

    prompt_path = (
        Path(__file__).resolve().parents[1]
        / "core"
        / "prompt.txt"
    )

    try:

        prompt = prompt_path.read_text(
            encoding="utf-8"
        ).strip()

    except Exception:

        prompt = (
            "You are JARVIS, a helpful personal AI assistant. "
            "Speak naturally and concisely."
        )

    return (
        prompt
        + "\n\n"
        "LIVE CONVERSATION MODE: "
        "Have a natural spoken conversation. "
        "Do not require a wake word between turns. "
        "Allow the user to interrupt you. "
        "Keep responses conversational and concise. "
        "If the user clearly says a live-mode exit phrase "
        "such as 'stop live conversation', stop the live "
        "conversation immediately."
    )


# ============================================================
# LIVE CONVERSATION
# ============================================================

class LiveConversation:

    def __init__(self):

        self._thread = None

        self._stop_event = (
            threading.Event()
        )

        self._running = False

        self._stopping = False

        self._state_lock = (
            threading.Lock()
        )

    # ========================================================
    # STATUS
    # ========================================================

    @property
    def running(self):

        with self._state_lock:

            return self._running

    # ========================================================
    # START
    # ========================================================

    def start(self):

        with self._state_lock:

            if self._running:

                print(
                    "[LIVE] Already running."
                )

                return False

        if not _api_key():

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        print(
            "[LIVE] Starting Live Conversation..."
        )

        # ----------------------------------------------------
        # Give Gemini exclusive microphone ownership.
        # ----------------------------------------------------

        pause_listener()

        self._stop_event.clear()

        self._stopping = False

        self._thread = (
            threading.Thread(
                target=self._thread_main,
                daemon=True,
                name=(
                    "JARVIS-LiveConversation"
                ),
            )
        )

        self._thread.start()

        return True

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        was_running = self.running

        self._stopping = True

        self._stop_event.set()

        if was_running:

            print(
                "[LIVE] Stopping Live Conversation..."
            )

        else:

            # Even if the session already died,
            # make sure normal JARVIS can resume.

            resume_listener()

        return was_running

    # ========================================================
    # THREAD
    # ========================================================

    def _thread_main(self):

        try:

            asyncio.run(
                self._run()
            )

        except Exception as exc:

            if self._stopping:

                print(
                    "[LIVE] Live session closed."
                )

            else:

                print(
                    "[LIVE] Conversation stopped: "
                    f"{exc}"
                )

        finally:

            with self._state_lock:

                self._running = False

            self._stopping = False

            # ------------------------------------------------
            # ALWAYS return microphone ownership to normal
            # JARVIS.
            # ------------------------------------------------

            resume_listener()

            print(
                "[LIVE] Normal JARVIS microphone resumed."
            )

    # ========================================================
    # LIVE SESSION
    # ========================================================

    async def _run(self):

        with self._state_lock:

            self._running = True

        client = genai.Client(
            api_key=_api_key(),
            http_options={
                "api_version": "v1beta"
            },
        )

        config = types.LiveConnectConfig(

            response_modalities=[
                "AUDIO"
            ],

            input_audio_transcription={},

            output_audio_transcription={},

            system_instruction=(
                _system_prompt()
            ),

            speech_config=(
                types.SpeechConfig(
                    voice_config=(
                        types.VoiceConfig(
                            prebuilt_voice_config=(
                                types.PrebuiltVoiceConfig(
                                    voice_name="Charon"
                                )
                            )
                        )
                    )
                )
            ),
        )

        audio_out = (
            asyncio.Queue()
        )

        loop = (
            asyncio.get_running_loop()
        )

        audio_in = (
            asyncio.Queue(
                maxsize=200
            )
        )

        # ====================================================
        # MICROPHONE CALLBACK
        # ====================================================

        def mic_callback(
            indata,
            frames,
            time_info,
            status,
        ):

            if self._stop_event.is_set():

                return

            try:

                loop.call_soon_threadsafe(
                    audio_in.put_nowait,
                    {
                        "data":
                            indata.tobytes(),

                        "mime_type":
                            "audio/pcm",
                    },
                )

            except Exception:

                pass

        # ====================================================
        # GEMINI SESSION
        # ====================================================

        async with client.aio.live.connect(
            model=LIVE_MODEL,
            config=config,
        ) as session:

            print(
                "[LIVE] Gemini Live connected."
            )

            # =================================================
            # SEND MICROPHONE
            # =================================================

            async def send_mic():

                try:

                    with sd.InputStream(
                        samplerate=INPUT_RATE,
                        channels=CHANNELS,
                        dtype="int16",
                        blocksize=BLOCK_SIZE,
                        callback=mic_callback,
                    ):

                        print(
                            "[LIVE] Microphone active."
                        )

                        while not self._stop_event.is_set():

                            try:

                                msg = (
                                    await asyncio.wait_for(
                                        audio_in.get(),
                                        timeout=0.2,
                                    )
                                )

                            except asyncio.TimeoutError:

                                continue

                            await session.send_realtime_input(
                                media=msg
                            )

                except Exception as exc:

                    if not self._stopping:

                        print(
                            "[LIVE] Microphone error: "
                            f"{exc}"
                        )

                    self._stop_event.set()

            # =================================================
            # RECEIVE GEMINI AUDIO
            # =================================================

            async def receive_audio():

                stream = (
                    sd.RawOutputStream(
                        samplerate=OUTPUT_RATE,
                        channels=CHANNELS,
                        dtype="int16",
                        blocksize=BLOCK_SIZE,
                    )
                )

                stream.start()

                try:

                    async for response in session.receive():

                        if self._stop_event.is_set():

                            break

                        # -------------------------------------
                        # Native Gemini audio
                        # -------------------------------------

                        if response.data:

                            await asyncio.to_thread(
                                stream.write,
                                response.data,
                            )

                        # -------------------------------------
                        # Server content
                        # -------------------------------------

                        server_content = (
                            response.server_content
                        )

                        if not server_content:

                            continue

                        # -------------------------------------
                        # USER TRANSCRIPTION
                        # -------------------------------------

                        input_text = ""

                        if (
                            server_content.input_transcription
                            and
                            server_content
                            .input_transcription
                            .text
                        ):

                            input_text = (
                                server_content
                                .input_transcription
                                .text
                            )

                            print(
                                "[YOU]",
                                input_text,
                            )

                            # ---------------------------------
                            # VOICE EXIT COMMAND
                            # ---------------------------------

                            if self._is_stop_phrase(
                                input_text
                            ):

                                print(
                                    "[LIVE] "
                                    "Voice stop command detected."
                                )

                                self._stop_event.set()

                                break

                        # -------------------------------------
                        # JARVIS TRANSCRIPTION
                        # -------------------------------------

                        if (
                            server_content.output_transcription
                            and
                            server_content
                            .output_transcription
                            .text
                        ):

                            print(
                                "[JARVIS]",
                                server_content
                                .output_transcription
                                .text,
                            )

                finally:

                    stream.stop()

                    stream.close()

            # =================================================
            # RUN AUDIO LOOPS
            # =================================================

            await asyncio.gather(
                send_mic(),
                receive_audio(),
            )

            print(
                "[LIVE] Gemini Live session ending."
            )

    # ========================================================
    # STOP PHRASE DETECTION
    # ========================================================

    @staticmethod
    def _is_stop_phrase(
        text: str,
    ) -> bool:

        normalized = (
            " ".join(
                text.lower().split()
            )
        )

        for phrase in _STOP_PHRASES:

            if phrase in normalized:

                return True

        return False


# ============================================================
# GLOBAL LIVE INSTANCE
# ============================================================

_live = LiveConversation()


# ============================================================
# REGISTRY ACTIONS
# ============================================================

def start_live_conversation(
    _data=None,
):

    started = (
        _live.start()
    )

    if not started:

        return (
            "Live conversation is already running."
        )

    return (
        "Live conversation started. "
        "You can speak naturally without "
        "repeating the wake word."
    )


def stop_live_conversation(
    _data=None,
):

    stopped = (
        _live.stop()
    )

    if not stopped:

        return (
            "Live conversation is already stopped."
        )

    return (
        "Live conversation stopped."
    )


def live_conversation_status(
    _data=None,
):

    if _live.running:

        return (
            "Live conversation is running."
        )

    return (
        "Live conversation is stopped."
    )