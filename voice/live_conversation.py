"""
JARVIS PRO - Natural Live Conversation
Mark-L-main Gemini Native Audio concept adapted as an OPTIONAL
voice mode.

Place at:
    voice/live_conversation.py

This does NOT replace:
    voice.manager
    voice.online_runner
    core.listener
    existing NCI

Run it only when the user explicitly starts Live Conversation.
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
import time
from pathlib import Path

from core.listener import (
    pause_listener,
    resume_listener,
)

import sounddevice as sd

try:
    from google import genai
    from google.genai import types
except ImportError as exc:
    raise RuntimeError(
        "Install google-genai before using Live Conversation: "
        "pip install google-genai"
    ) from exc


LIVE_MODEL = os.getenv(
    "JARVIS_LIVE_MODEL",
    "models/gemini-2.5-flash-native-audio-preview-12-2025",
)

INPUT_RATE = 16000
OUTPUT_RATE = 24000
CHANNELS = 1
BLOCK_SIZE = 1024


def _api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()

    if key:
        return key

    # Optional fallback to the existing JARVIS config.
    config_path = (
        Path(__file__).resolve().parents[1]
        / "config"
        / "api_keys.json"
    )

    try:
        data = json.loads(
            config_path.read_text(encoding="utf-8")
        )
        return str(
            data.get("gemini_api_key", "")
        ).strip()
    except Exception:
        return ""


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
        "Keep responses conversational and concise."
    )


class LiveConversation:
    """
    Gemini Native Audio session.

    Usage:
        live = LiveConversation()
        live.start()
        ...
        live.stop()
    """

    def __init__(self):
        self._thread = None
        self._stop_event = threading.Event()
        self._running = False

    @property
    def running(self):
        return self._running

    def start(self):

        if self._running:

            return

        if not _api_key():

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        # Give the Gemini Live microphone exclusive
        # ownership while Live Conversation is active.

        pause_listener()

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._thread_main,
            daemon=True,
            name="JARVIS-LiveConversation",
        )

        self._thread.start()

    def stop(self):

        self._stop_event.set()

        self._running = False

        # Give the normal JARVIS microphone back
        # after Gemini Live releases its microphone.

        resume_listener()

    def _thread_main(self):

        try:

            asyncio.run(
                self._run()
            )

        except Exception as exc:

            print(
                f"[LIVE] Conversation stopped: {exc}"
            )

        finally:

            self._running = False

            # Always return microphone ownership
            # to normal JARVIS.

            resume_listener()

    async def _run(self):
        self._running = True

        client = genai.Client(
            api_key=_api_key(),
            http_options={"api_version": "v1beta"},
        )

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            input_audio_transcription={},
            output_audio_transcription={},
            system_instruction=_system_prompt(),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Charon"
                    )
                )
            ),
        )

        audio_out = asyncio.Queue()
        loop = asyncio.get_running_loop()

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
                        "data": indata.tobytes(),
                        "mime_type": "audio/pcm",
                    },
                )
            except Exception:
                pass

        audio_in = asyncio.Queue(maxsize=200)

        async with client.aio.live.connect(
            model=LIVE_MODEL,
            config=config,
        ) as session:

            async def send_mic():
                with sd.InputStream(
                    samplerate=INPUT_RATE,
                    channels=CHANNELS,
                    dtype="int16",
                    blocksize=BLOCK_SIZE,
                    callback=mic_callback,
                ):
                    while not self._stop_event.is_set():
                        try:
                            msg = await asyncio.wait_for(
                                audio_in.get(),
                                timeout=0.2,
                            )
                        except asyncio.TimeoutError:
                            continue

                        await session.send_realtime_input(
                            media=msg
                        )

            async def receive_audio():
                stream = sd.RawOutputStream(
                    samplerate=OUTPUT_RATE,
                    channels=CHANNELS,
                    dtype="int16",
                    blocksize=BLOCK_SIZE,
                )
                stream.start()

                try:
                    async for response in session.receive():
                        if self._stop_event.is_set():
                            break

                        if response.data:
                            await asyncio.to_thread(
                                stream.write,
                                response.data,
                            )

                        sc = response.server_content

                        if sc:
                            if (
                                sc.input_transcription
                                and sc.input_transcription.text
                            ):
                                print(
                                    "[YOU]",
                                    sc.input_transcription.text,
                                )

                            if (
                                sc.output_transcription
                                and sc.output_transcription.text
                            ):
                                print(
                                    "[JARVIS]",
                                    sc.output_transcription.text,
                                )

                finally:
                    stream.stop()
                    stream.close()

            await asyncio.gather(
                send_mic(),
                receive_audio(),
            )


_live = LiveConversation()


def start_live_conversation(_data=None):
    _live.start()
    return (
        "Live conversation started. "
        "You can speak naturally without repeating the wake word."
    )


def stop_live_conversation(_data=None):
    _live.stop()
    return "Live conversation stopped."


def live_conversation_status(_data=None):
    return (
        "Live conversation is running."
        if _live.running
        else "Live conversation is stopped."
    )
