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

from core.dispatcher import dispatch
from core.live_execution import live_execution

from hud.integration import HUDIntegration

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

# 1024 samples at 16 kHz ~= 64 ms.
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
    Load the existing JARVIS prompt and add only the
    Live Conversation behavior rules.
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

    live_rules = """
=============================================================
LIVE CONVERSATION BEHAVIOR
=============================================================

You are JARVIS in a natural realtime spoken conversation.

GENERAL BEHAVIOR
- Speak naturally, calmly, and conversationally.
- Do not require a wake word between turns.
- Treat every clearly new user utterance as a new turn.
- Preserve conversation context when the user is clearly
  continuing the previous topic.
- Do not invent a connection between unrelated short inputs.
- If the user's new request is clear, answer it directly.

RESPONSE STYLE
- Keep spoken answers concise unless the user asks for detail.
- Usually answer in one or a few natural sentences.
- Do not repeatedly say:
  "Anything else?"
  "How can I help you today?"
  "What else can I do for you?"
- Do not append a generic question after every answer.
- After answering, naturally stop and wait for the next turn.
- Do not repeat information that was already given.
- Do not continue speaking after the answer is complete.

SHORT INPUTS
- Short inputs such as numbers, names, or brief phrases may be
  follow-up answers, but do not automatically assume they are.
- Use the current conversational context to interpret them.
- If a short input does not clearly continue the previous topic,
  respond naturally rather than repeating the previous answer.

INTERRUPTION
- Allow the user to speak naturally between responses.
- Never require the user to wait for a wake word.

REALTIME LIMITATIONS
- Do not claim to have live web/news access unless such access
  is actually available in this Live session.
- If the user asks for information requiring real-time data,
  clearly say that Live Conversation does not currently have
  that external data source instead of pretending.

STOP COMMAND
- If the user says "stop live conversation", stop the Live
  conversation immediately.
- Equivalent commands such as "end live conversation" or
  "exit live conversation" should also be understood.

IMPORTANT:
This is a spoken conversation. Favor natural short answers
over long assistant-style paragraphs.

JARVIS COMPUTER COMMANDS

You are connected to the JARVIS computer-control system.

When the user asks you to perform an action on the computer,
use the jarvis_command tool instead of pretending that you
performed the action yourself.

Examples:

- "Open YouTube"
- "Take a screenshot"
- "Open Spotify"
- "Turn the volume down"
- "Search YouTube for Python tutorials"
- "Show my battery"
- "Open Chrome"

For ordinary questions such as:

- "What is 2 + 2?"
- "What is the capital of India?"
- "Tell me something interesting."

answer normally without calling the tool.

Never claim that a computer action was completed unless the
jarvis_command tool was actually executed successfully.

After a command is executed, briefly tell the user the result
naturally.

"""

    return (
        prompt
        + "\n\n"
        + live_rules
    )


# =============================================================
# JARVIS COMMAND TOOL
# =============================================================

JARVIS_COMMAND_TOOL = {
    "function_declarations": [
        {
            "name": "jarvis_command",
            "description": (
                "Execute a command using the existing JARVIS "
                "command system. Use this only when the user "
                "is asking JARVIS to perform an action on the "
                "computer or use one of its installed skills. "
                "Do not use it for ordinary questions or casual "
                "conversation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "The user's intended JARVIS command "
                            "in natural language."
                        ),
                    }
                },
                "required": [
                    "command"
                ],
            },
        }
    ]
}


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
        
                # -----------------------------------------------------
        # Live microphone state.
        #
        # This is separate from the normal JARVIS listener.
        # Turning the HUD microphone OFF while Live is running
        # must silence Live input without closing the session.
        # -----------------------------------------------------

        self._microphone_enabled = True

        self._microphone_lock = threading.Lock()

        # -----------------------------------------------------
        # Prevent duplicate pause/resume operations.
        #
        # This is intentionally owned by LiveConversation so
        # repeated calls cannot pause/resume the normal listener
        # multiple times.
        # -----------------------------------------------------

        self._normal_mic_paused = False

        self._normal_mic_lock = threading.Lock()

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
    # LIVE MICROPHONE STATE
    # =========================================================

    def set_microphone_enabled(
        self,
        enabled: bool,
    ):

        with self._microphone_lock:

            self._microphone_enabled = bool(
                enabled
            )

        print(
            "[LIVE] Microphone:",
            "ON" if enabled else "OFF",
        )

    # ---------------------------------------------------------

    def microphone_enabled(self) -> bool:

        with self._microphone_lock:

            return self._microphone_enabled

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
        
        self.set_microphone_enabled(True)

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
        # Pause the normal JARVIS microphone exactly once.
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

        # =====================================================
        # GEMINI LIVE CONFIGURATION
        # =====================================================

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
            
            tools=[
                JARVIS_COMMAND_TOOL
            ],

            speech_config=types.SpeechConfig(

                voice_config=types.VoiceConfig(

                    prebuilt_voice_config=(
                        types.PrebuiltVoiceConfig(
                            voice_name="Charon"
                        )
                    )

                )

            ),

            # Keep reasoning lightweight for realtime speech.
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

            # -------------------------------------------------
            # HUD microphone switch.
            #
            # Live session remains connected while the
            # microphone is OFF. Only audio input is muted.
            # -------------------------------------------------

            if not self.microphone_enabled():

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
                # MICROPHONE
                # =============================================

                microphone = sd.RawInputStream(

                    samplerate=INPUT_RATE,

                    channels=CHANNELS,

                    dtype=DTYPE,

                    blocksize=BLOCK_SIZE,

                    callback=microphone_callback,
                )

                # =============================================
                # SPEAKER
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
                # AUDIO SENDER
                # =============================================

                sender_task = asyncio.create_task(
                    self._send_audio(
                        session,
                        input_queue,
                    ),
                    name="JARVIS-LiveAudioSender",
                )

                # =============================================
                # STOP WATCHER
                # =============================================

                stop_task = asyncio.create_task(
                    self._wait_for_stop(),
                    name="JARVIS-LiveStopWatcher",
                )

                try:

                    # =========================================
                    # PERSISTENT RECEIVE LOOP
                    # =========================================
                    #
                    # One Gemini session.
                    #
                    # receive() handles one model turn.
                    #
                    # When that turn finishes, we call
                    # receive() again on the SAME session.
                    #
                    # There is NO reconnect here.
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
                        # STOP REQUEST
                        # -------------------------------------

                        if stop_task in done:

                            self._stop_event.set()

                            if not receive_task.done():

                                receive_task.cancel()

                            await asyncio.gather(
                                receive_task,
                                return_exceptions=True,
                            )

                            break

                        # -------------------------------------
                        # GEMINI TURN FINISHED
                        # -------------------------------------

                        if receive_task in done:

                            try:

                                result = (
                                    receive_task.result()
                                )

                                if result in (
                                    "session_closed",
                                    "stop_requested",
                                    "stopped",
                                ):

                                    break

                                # --------------------------------
                                # "turn_complete" is expected.
                                #
                                # DO NOT close the session.
                                # --------------------------------

                                if result == "turn_complete":

                                    continue

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
            # RESUME NORMAL JARVIS MICROPHONE
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

            # Drop oldest audio chunk to keep latency bounded.

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
                # DO NOT send audio_stream_end after each phrase.
                #
                # Gemini's automatic VAD handles speech turns.
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

        Returning from this function does NOT terminate
        Live Conversation.

        The SAME Gemini session remains alive.

        The caller invokes this method again.
        """

        try:

            async for response in session.receive():
                
                # =============================================
                # JARVIS TOOL CALL
                # =============================================

                if response.tool_call:

                    function_responses = []

                    for function_call in (
                        response.tool_call.function_calls
                    ):

                        function_name = (
                            function_call.name
                        )

                        print(
                            "[LIVE TOOL]",
                            function_name,
                        )

                        # -----------------------------------------
                        # JARVIS COMMAND
                        # -----------------------------------------

                        if function_name == "jarvis_command":

                            args = (
                                function_call.args
                                or {}
                            )

                            command = str(
                                args.get(
                                    "command",
                                    "",
                                )
                            ).strip()

                            print(
                                "[LIVE TOOL COMMAND]",
                                command,
                            )

                            if not command:

                                result = {
                                    "success": False,
                                    "message": (
                                        "No JARVIS command was provided."
                                    ),
                                }

                            else:

                                try:

                                    # ---------------------------------
                                    # Existing JARVIS dispatcher
                                    # remains authoritative.
                                    # ---------------------------------

                                    with live_execution():

                                        dispatch(
                                            command
                                        )

                                    result = {
                                        "success": True,
                                        "message": (
                                            f"JARVIS executed: {command}"
                                        ),
                                    }

                                except Exception as exc:

                                    print(
                                        "[LIVE TOOL ERROR]",
                                        exc,
                                    )

                                    result = {
                                        "success": False,
                                        "message": str(
                                            exc
                                        ),
                                    }

                        else:

                            result = {
                                "success": False,
                                "message": (
                                    f"Unknown JARVIS tool: "
                                    f"{function_name}"
                                ),
                            }

                        function_responses.append(
                            types.FunctionResponse(
                                id=function_call.id,
                                name=function_name,
                                response=result,
                            )
                        )

                    # ---------------------------------------------
                    # Send result back to Gemini.
                    # ---------------------------------------------

                    await session.send_tool_response(
                        function_responses=function_responses
                    )

                    continue

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
                        # LOCAL STOP COMMAND
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
                    # Only this receive operation ends.
                    #
                    # Gemini session remains alive.
                    #
                    # _run() calls receive() again.
                    # -----------------------------------------

                    return "turn_complete"

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
            .replace(
                "?",
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
            command == normalized
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

    def _pause_normal_microphone(self):
        """
        Pause the normal JARVIS listener exactly once.

        This prevents duplicate calls if the Live action is
        triggered while another part of JARVIS has already
        initiated the pause.
        """

        with self._normal_mic_lock:

            if self._normal_mic_paused:

                print(
                    "[MIC] Background listener already paused"
                )

                return

            try:

                from core.listener import (
                    pause_listener,
                )

                pause_listener()

                self._normal_mic_paused = True

            except ImportError:

                print(
                    "[MIC] Background listener pause API unavailable."
                )

            except Exception as exc:

                print(
                    "[MIC] Could not pause listener:",
                    exc,
                )

    def _resume_normal_microphone(self):
        """
        Resume the normal JARVIS listener exactly once.
        """

        with self._normal_mic_lock:

            if not self._normal_mic_paused:

                print(
                    "[MIC] Background listener already resumed"
                )

                return

            try:

                from core.listener import (
                    resume_listener,
                )

                resume_listener()

                self._normal_mic_paused = False

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

    try:

        HUDIntegration.system_activity(
            "LIVE CONVERSATION ON"
        )

    except Exception as exc:

        print(
            "[HUD LIVE CONVERSATION LOG ERROR]",
            exc,
        )

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

    try:

        HUDIntegration.system_activity(
            "LIVE CONVERSATION OFF"
        )

    except Exception as exc:

        print(
            "[HUD LIVE CONVERSATION LOG ERROR]",
            exc,
        )

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