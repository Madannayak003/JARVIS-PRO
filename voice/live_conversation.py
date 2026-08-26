"""
=============================================================
JARVIS PRO — LIVE CONVERSATION
=============================================================

Gemini Live native-audio conversation.

IMPORTANT ARCHITECTURE:

    Normal JARVIS microphone
            |
            | start_live_conversation
            v
    pause normal listener
            |
            v
    ONE persistent Gemini Live session
            |
       +----+----+
       |         |
       v         v
   microphone   speaker
       |         ^
       v         |
      Gemini Live
       |
       +--> receive() completes one TURN
                |
                +--> receive() AGAIN
                |
                +--> receive() AGAIN
                |
                +--> receive() AGAIN
                |
               ...

The Gemini session itself is NOT recreated between turns.

No custom VAD.
No reconnect loop.
No session-resumption loop.
No audio_stream_end after every utterance.

Normal JARVIS architecture remains untouched outside Live mode.
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
from pathlib import Path
from typing import Optional

import sounddevice as sd

from google import genai
from google.genai import types


# =============================================================
# CONFIGURATION
# =============================================================

DEFAULT_MODEL = "gemini-3.1-flash-live-preview"

LIVE_MODEL = os.getenv(
    "JARVIS_LIVE_MODEL",
    DEFAULT_MODEL,
)

INPUT_RATE = 16000
OUTPUT_RATE = 24000

CHANNELS = 1

DTYPE = "int16"

# 1024 samples at 16 kHz ~= 64 ms
# This gives a good latency/CPU balance.
BLOCK_SIZE = 1024

INPUT_QUEUE_SIZE = 64


# =============================================================
# API KEY
# =============================================================

def _api_key() -> str:
    """
    Resolve Gemini API key.

    Priority:

        1. GEMINI_API_KEY
        2. config/api_keys.json
    """

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


# =============================================================
# SYSTEM PROMPT
# =============================================================

def _system_prompt() -> str:
    """
    Reuse the existing JARVIS prompt.
    """

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
            "You are JARVIS, a helpful personal AI assistant."
        )

    return (
        prompt
        + "\n\n"
        "LIVE CONVERSATION MODE:\n"
        "You are JARVIS in a natural realtime spoken conversation.\n"
        "Do not require a wake word between turns.\n"
        "Listen for the user's next request continuously.\n"
        "Keep spoken responses concise and natural.\n"
        "Do not repeatedly say 'How can I help you today?'.\n"
        "Do not unnecessarily repeat yourself.\n"
        "Allow the user to interrupt you naturally.\n"
        "Treat each new user utterance as the next conversational turn.\n"
        "If the user says 'stop live conversation', end the live conversation."
    )


# =============================================================
# LIVE CONVERSATION CLASS
# =============================================================

class LiveConversation:

    def __init__(self):

        self._thread: Optional[
            threading.Thread
        ] = None

        self._stop_event = threading.Event()

        self._state_lock = threading.Lock()

        self._running = False

    # =========================================================
    # STATE
    # =========================================================

    @property
    def running(self) -> bool:

        with self._state_lock:

            return self._running

    def _set_running(
        self,
        value: bool,
    ):

        with self._state_lock:

            self._running = value

    # =========================================================
    # START
    # =========================================================

    def start(self):

        if self.running:

            print(
                "[LIVE] Already running."
            )

            return

        if not _api_key():

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._thread_main,
            daemon=True,
            name="JARVIS-LiveConversation",
        )

        self._thread.start()

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        if not self.running:

            print(
                "[LIVE] Already stopped."
            )

            return

        print(
            "[LIVE] Stop requested."
        )

        self._stop_event.set()

    # =========================================================
    # THREAD ENTRY
    # =========================================================

    def _thread_main(self):

        self._set_running(True)

        try:

            asyncio.run(
                self._run()
            )

        except Exception as exc:

            print(
                f"[LIVE] Fatal error: {exc}"
            )

        finally:

            self._set_running(False)

            print(
                "[LIVE] Live Conversation ended."
            )

    # =========================================================
    # MAIN SESSION
    # =========================================================

    async def _run(self):

        api_key = _api_key()

        if not api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        print(
            "[LIVE] Starting Live Conversation..."
        )

        print(
            f"[LIVE] Model: {LIVE_MODEL}"
        )

        # -----------------------------------------------------
        # Pause the normal JARVIS listener BEFORE opening
        # the Live microphone.
        # -----------------------------------------------------

        self._pause_normal_microphone()

        input_queue: asyncio.Queue[
            bytes
        ] = asyncio.Queue(
            maxsize=INPUT_QUEUE_SIZE
        )

        loop = asyncio.get_running_loop()

        microphone = None
        speaker = None

        client = genai.Client(
            api_key=api_key
        )

        # -----------------------------------------------------
        # Gemini Live configuration
        #
        # Automatic VAD is intentionally left enabled.
        # Gemini handles speech turn detection.
        # -----------------------------------------------------

        config = types.LiveConnectConfig(

            response_modalities=[
                types.Modality.AUDIO
            ],

            input_audio_transcription=(
                types.AudioTranscriptionConfig()
            ),

            output_audio_transcription=(
                types.AudioTranscriptionConfig()
            ),

            system_instruction=types.Content(
                parts=[
                    types.Part(
                        text=_system_prompt()
                    )
                ]
            ),

            speech_config=types.SpeechConfig(

                voice_config=types.VoiceConfig(

                    prebuilt_voice_config=(
                        types.PrebuiltVoiceConfig(
                            voice_name="Charon"
                        )
                    )

                )

            ),

            # Keep thinking minimal for realtime response.
            thinking_config=types.ThinkingConfig(
                thinking_level="minimal"
            ),
        )

        # =====================================================
        # MICROPHONE CALLBACK
        # =====================================================

        def microphone_callback(
            indata,
            frames,
            time_info,
            status,
        ):

            if self._stop_event.is_set():

                return

            if status:

                print(
                    f"[LIVE] Microphone status: {status}"
                )

            try:

                audio_bytes = bytes(
                    indata
                )

                loop.call_soon_threadsafe(
                    self._queue_audio,
                    input_queue,
                    audio_bytes,
                )

            except Exception as exc:

                print(
                    "[LIVE] Microphone callback error:",
                    exc,
                )

        try:

            # =================================================
            # CONNECT ONCE
            # =================================================

            async with client.aio.live.connect(
                model=LIVE_MODEL,
                config=config,
            ) as session:

                print(
                    "[LIVE] Gemini Live connected."
                )

                # =============================================
                # OPEN MICROPHONE
                # =============================================

                microphone = sd.RawInputStream(

                    samplerate=INPUT_RATE,

                    channels=CHANNELS,

                    dtype=DTYPE,

                    blocksize=BLOCK_SIZE,

                    callback=microphone_callback,
                )

                # =============================================
                # OPEN SPEAKER
                # =============================================

                speaker = sd.RawOutputStream(

                    samplerate=OUTPUT_RATE,

                    channels=CHANNELS,

                    dtype=DTYPE,

                    blocksize=BLOCK_SIZE,
                )

                microphone.start()

                speaker.start()

                print(
                    "[LIVE] Microphone active."
                )

                print(
                    "[LIVE] Speaker active."
                )

                # =============================================
                # START AUDIO SENDER
                # =============================================

                sender_task = asyncio.create_task(
                    self._send_audio(
                        session,
                        input_queue,
                    ),
                    name="JARVIS-LiveAudioSender",
                )

                # =============================================
                # START STOP WATCHER
                # =============================================

                stop_task = asyncio.create_task(
                    self._wait_for_stop(),
                    name="JARVIS-LiveStopWatcher",
                )

                try:

                    # =========================================
                    # IMPORTANT:
                    #
                    # session.receive() completes after ONE
                    # model turn.
                    #
                    # Therefore we call it AGAIN for the
                    # next turn WITHOUT reconnecting.
                    # =========================================

                    while not self._stop_event.is_set():

                        receive_task = asyncio.create_task(
                            self._receive_one_turn(
                                session,
                                speaker,
                            ),
                            name="JARVIS-LiveReceiveTurn",
                        )

                        done, pending = await asyncio.wait(
                            {
                                receive_task,
                                stop_task,
                            },
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                        # -------------------------------------
                        # Stop requested
                        # -------------------------------------

                        if stop_task in done:

                            self._stop_event.set()

                            receive_task.cancel()

                            await asyncio.gather(
                                receive_task,
                                return_exceptions=True,
                            )

                            break

                        # -------------------------------------
                        # One Gemini turn completed.
                        #
                        # DO NOT CLOSE SESSION.
                        #
                        # Simply loop and call receive()
                        # again.
                        # -------------------------------------

                        if receive_task in done:

                            try:

                                result = (
                                    receive_task.result()
                                )

                                if result == "session_closed":

                                    print(
                                        "[LIVE] Gemini session closed."
                                    )

                                    break

                            except asyncio.CancelledError:

                                break

                            except Exception as exc:

                                print(
                                    "[LIVE] Receive turn error:",
                                    exc,
                                )

                                break

                finally:

                    stop_task.cancel()

                    sender_task.cancel()

                    await asyncio.gather(
                        stop_task,
                        sender_task,
                        return_exceptions=True,
                    )

        finally:

            # =================================================
            # CLOSE MICROPHONE
            # =================================================

            if microphone is not None:

                try:

                    microphone.stop()

                except Exception:
                    pass

                try:

                    microphone.close()

                except Exception:
                    pass

            # =================================================
            # CLOSE SPEAKER
            # =================================================

            if speaker is not None:

                try:

                    speaker.stop()

                except Exception:
                    pass

                try:

                    speaker.close()

                except Exception:
                    pass

            print(
                "[LIVE] Audio devices closed."
            )

            # =================================================
            # RESUME NORMAL JARVIS LISTENER
            # =================================================

            self._resume_normal_microphone()

            print(
                "[LIVE] Normal JARVIS microphone resumed."
            )

    # =========================================================
    # QUEUE AUDIO
    # =========================================================

    @staticmethod
    def _queue_audio(
        queue: asyncio.Queue,
        audio: bytes,
    ):

        try:

            queue.put_nowait(
                audio
            )

        except asyncio.QueueFull:

            # Drop the oldest chunk to keep latency bounded.

            try:

                queue.get_nowait()

            except asyncio.QueueEmpty:
                pass

            try:

                queue.put_nowait(
                    audio
                )

            except asyncio.QueueFull:
                pass

    # =========================================================
    # SEND AUDIO
    # =========================================================

    async def _send_audio(
        self,
        session,
        input_queue: asyncio.Queue,
    ):

        try:

            while not self._stop_event.is_set():

                try:

                    audio = await asyncio.wait_for(
                        input_queue.get(),
                        timeout=0.25,
                    )

                except asyncio.TimeoutError:

                    continue

                # ------------------------------------------------
                # IMPORTANT:
                #
                # Do NOT send audio_stream_end after each phrase.
                #
                # Gemini's automatic VAD handles the turns.
                # ------------------------------------------------

                await session.send_realtime_input(

                    audio=types.Blob(
                        data=audio,
                        mime_type=(
                            "audio/pcm;rate=16000"
                        ),
                    )

                )

        except asyncio.CancelledError:

            raise

        except Exception as exc:

            print(
                "[LIVE] Audio sender stopped:",
                exc,
            )

            self._stop_event.set()

            raise

    # =========================================================
    # RECEIVE ONE GEMINI TURN
    # =========================================================

    async def _receive_one_turn(
        self,
        session,
        speaker,
    ):
        """
        Receive exactly ONE Gemini model turn.

        IMPORTANT:

        This function ending does NOT mean Live Conversation
        should end.

        The caller invokes it again using the SAME session.
        """

        try:

            async for response in session.receive():

                if self._stop_event.is_set():

                    return "stopped"

                # =============================================
                # AUDIO OUTPUT
                # =============================================

                if response.data:

                    await asyncio.to_thread(
                        speaker.write,
                        response.data,
                    )

                # =============================================
                # SERVER CONTENT
                # =============================================

                server_content = (
                    response.server_content
                )

                if not server_content:

                    continue

                # =============================================
                # USER TRANSCRIPTION
                # =============================================

                input_transcription = (
                    server_content.input_transcription
                )

                if (
                    input_transcription
                    and input_transcription.text
                ):

                    user_text = (
                        input_transcription.text.strip()
                    )

                    if user_text:

                        print(
                            "[YOU]",
                            user_text,
                        )

                        # -------------------------------------
                        # LOCAL LIVE-MODE STOP COMMAND
                        #
                        # Normal JARVIS microphone is paused,
                        # so Live mode itself must be capable
                        # of stopping.
                        # -------------------------------------

                        if self._is_stop_command(
                            user_text
                        ):

                            print(
                                "[LIVE] Stop command detected."
                            )

                            self._stop_event.set()

                            return "stop_requested"

                # =============================================
                # JARVIS TRANSCRIPTION
                # =============================================

                output_transcription = (
                    server_content.output_transcription
                )

                if (
                    output_transcription
                    and output_transcription.text
                ):

                    output_text = (
                        output_transcription.text.strip()
                    )

                    if output_text:

                        print(
                            "[JARVIS]",
                            output_text,
                        )

                # =============================================
                # TURN COMPLETE
                # =============================================

                if getattr(
                    server_content,
                    "turn_complete",
                    False,
                ):

                    print(
                        "[LIVE] Turn complete."
                    )

                    # -----------------------------------------
                    # CRITICAL:
                    #
                    # Return from this function only.
                    #
                    # The Gemini SESSION remains open.
                    #
                    # _run() immediately calls
                    # _receive_one_turn() again.
                    # -----------------------------------------

                    return "turn_complete"

            # async generator ended without a normal turn.

            return "session_closed"

        except asyncio.CancelledError:

            raise

        except Exception as exc:

            print(
                "[LIVE] Gemini receive error:",
                exc,
            )

            self._stop_event.set()

            raise

    # =========================================================
    # STOP COMMAND DETECTION
    # =========================================================

    @staticmethod
    def _is_stop_command(
        text: str,
    ) -> bool:

        normalized = (
            text.lower()
            .strip()
            .replace(
                ".",
                "",
            )
            .replace(
                "!",
                "",
            )
        )

        stop_commands = (
            "stop live conversation",
            "stop the live conversation",
            "end live conversation",
            "end the live conversation",
            "exit live conversation",
            "exit the live conversation",
            "close live conversation",
            "close the live conversation",
        )

        return any(
            command in normalized
            for command in stop_commands
        )

    # =========================================================
    # STOP WATCHER
    # =========================================================

    async def _wait_for_stop(self):

        while not self._stop_event.is_set():

            await asyncio.sleep(
                0.1
            )

        return "stop requested"

    # =========================================================
    # NORMAL JARVIS MICROPHONE
    # =========================================================

    @staticmethod
    def _pause_normal_microphone():

        try:

            from core.listener import (
                pause_listener,
            )

            pause_listener()

            print(
                "[MIC] Background listener paused"
            )

        except ImportError:

            print(
                "[MIC] Background listener pause API unavailable."
            )

        except Exception as exc:

            print(
                "[MIC] Could not pause listener:",
                exc,
            )

    @staticmethod
    def _resume_normal_microphone():

        try:

            from core.listener import (
                resume_listener,
            )

            resume_listener()

            print(
                "[MIC] Background listener resumed"
            )

        except ImportError:

            print(
                "[MIC] Background listener resume API unavailable."
            )

        except Exception as exc:

            print(
                "[MIC] Could not resume listener:",
                exc,
            )


# =============================================================
# GLOBAL LIVE INSTANCE
# =============================================================

_live = LiveConversation()


# =============================================================
# REGISTRY ACTIONS
# =============================================================

def start_live_conversation(
    _data=None,
):

    if _live.running:

        return (
            "Live conversation is already running."
        )

    _live.start()

    return (
        "Live conversation started."
    )


def stop_live_conversation(
    _data=None,
):

    if not _live.running:

        return (
            "Live conversation is already stopped."
        )

    _live.stop()

    return (
        "Stopping live conversation."
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