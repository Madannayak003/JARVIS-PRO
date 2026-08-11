import time
import re

from ai.chat import ask_chat
from ai.memory_manager import learn

from core.context import add_message

from voice.manager import (
    start_speech_session,
)

from voice.tts_pipeline import (
    TTSPipeline,
)


# =========================================================
# Voice Text Cleaner
# =========================================================

def clean_for_speech(text):
    """
    Clean AI response for TTS only.

    The original AI response remains unchanged for:

    - chat history
    - memory
    - UI
    - screen context

    Only the spoken version is cleaned.
    """

    if not text:

        return ""

    text = str(text)

    # -----------------------------------------------------
    # Remove code fences
    # -----------------------------------------------------

    text = re.sub(
        r"```[\w+-]*",
        "",
        text
    )

    text = text.replace(
        "```",
        ""
    )

    # -----------------------------------------------------
    # Remove Markdown bold
    # -----------------------------------------------------

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    # -----------------------------------------------------
    # Remove Markdown underline
    # -----------------------------------------------------

    text = re.sub(
        r"__(.*?)__",
        r"\1",
        text
    )

    # -----------------------------------------------------
    # Remove Markdown italic
    # -----------------------------------------------------

    text = re.sub(
        r"(?<!\*)\*(?!\s)(.*?)(?<!\s)\*(?!\*)",
        r"\1",
        text
    )

    text = re.sub(
        r"(?<!_)_(?!\s)(.*?)(?<!_)_",
        r"\1",
        text
    )

    # -----------------------------------------------------
    # Remove Markdown headings
    # -----------------------------------------------------

    text = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # -----------------------------------------------------
    # Remove Markdown bullet markers
    # -----------------------------------------------------

    text = re.sub(
        r"^\s*[-*+]\s+",
        "",
        text,
        flags=re.MULTILINE
    )

    # -----------------------------------------------------
    # Remove numbered list markers
    # -----------------------------------------------------

    text = re.sub(
        r"^\s*\d+\.\s+",
        "",
        text,
        flags=re.MULTILINE
    )

    # -----------------------------------------------------
    # Clean excessive whitespace
    # -----------------------------------------------------

    text = re.sub(
        r"\n+",
        " ",
        text
    )

    text = re.sub(
        r"\s{2,}",
        " ",
        text
    )

    return text.strip()


# =========================================================
# Run Chat
# =========================================================

def run_chat(
    question,
    stop_event
):

    print(
        "[AI WORKER] Thinking..."
    )

    # =====================================================
    # Memory
    # =====================================================

    memory_result = learn(
        question
    )

    if memory_result["saved"]:

        print(
            "[MEMORY] Saved -> "
            f"{memory_result['key']} = "
            f"{memory_result['value']}"
        )

    elif memory_result.get(
        "already_known"
    ):

        print(
            "[MEMORY] Already known."
        )

    # =====================================================
    # Start AI Request
    # =====================================================

    t0 = time.perf_counter()

    session = ask_chat(
        question,
        stop_event
    )

    stream = session.stream

    is_developer = (
        session.is_developer
    )

    print(
        "Request sent:",
        time.perf_counter() - t0
    )

    # =====================================================
    # Response State
    # =====================================================

    answer = ""

    sentence_buffer = ""

    # =====================================================
    # TTS Pipeline
    # =====================================================

    voice_session = None

    tts_pipeline = None

    if not is_developer:

        # -------------------------------------------------
        # Create a NEW voice session for this response.
        # -------------------------------------------------

        voice_session = (
            start_speech_session()
        )

        # -------------------------------------------------
        # Create PRO TTS pipeline.
        #
        # Sentence generation and playback are now
        # separated so the next sentence can be prepared
        # while the current sentence is playing.
        # -------------------------------------------------

        tts_pipeline = TTSPipeline(

            stop_event=stop_event,

            session=voice_session,

        )

        tts_pipeline.start()

    # =====================================================
    # Developer Response Buffer
    # =====================================================

    developer_answer = ""

    # =====================================================
    # Stream AI Response
    # =====================================================

    try:

        first = True

        for data in stream:

            # -------------------------------------------------
            # Task interruption
            # -------------------------------------------------

            if stop_event.is_set():

                if first:

                    print(
                        "First token:",
                        time.perf_counter()
                        - t0
                    )

                    first = False

                print(
                    "\n[AI WORKER] Interrupted"
                )

                return

            # -------------------------------------------------
            # Extract token
            # -------------------------------------------------

            token = data.get(
                "response",
                ""
            )

            if not token:

                continue

            # -------------------------------------------------
            # Terminal output
            # -------------------------------------------------

            print(
                token,
                end="",
                flush=True
            )

            # -------------------------------------------------
            # Store complete answer
            # -------------------------------------------------

            answer += token

            # =================================================
            # Developer Mode
            # =================================================

            if is_developer:

                developer_answer += token

                continue

            # =================================================
            # Normal Chat
            # =================================================

            sentence_buffer += token

            # -------------------------------------------------
            # Extract complete sentences
            #
            # Decimal-safe:
            #
            # 1084.80
            # 2.44%
            #
            # will not be incorrectly split.
            # -------------------------------------------------

            while True:

                match = re.search(

                    r"""
                    (?<!\d)
                    [^.!?]+
                    [.!?]+
                    (?=\s|$)
                    """,

                    sentence_buffer,

                    re.VERBOSE

                )

                if not match:

                    break

                # -------------------------------------------------
                # Extract sentence
                # -------------------------------------------------

                sentence = (
                    match.group(0)
                    .strip()
                )

                # -------------------------------------------------
                # Remove extracted sentence
                # -------------------------------------------------

                sentence_buffer = (
                    sentence_buffer[
                        match.end():
                    ]
                )

                # -------------------------------------------------
                # Send to TTS pipeline
                # -------------------------------------------------

                if sentence:

                    cleaned = (
                        clean_for_speech(
                            sentence
                        )
                    )

                    if cleaned:

                        tts_pipeline.put(
                            cleaned
                        )

    finally:

        print()

    # =====================================================
    # Check Cancellation
    # =====================================================

    if stop_event.is_set():

        print(
            "[CHAT] Cancelled before TTS"
        )

        return

    if (
        voice_session
        and voice_session.cancel_event.is_set()
    ):

        print(
            "[CHAT] Voice session cancelled"
        )

        return

    # =====================================================
    # Remaining Text
    # =====================================================

    remaining = (
        sentence_buffer.strip()
    )

    if (
        remaining
        and not is_developer
    ):

        cleaned = (
            clean_for_speech(
                remaining
            )
        )

        if cleaned:

            tts_pipeline.put(
                cleaned
            )

    # =====================================================
    # Finish TTS Pipeline
    # =====================================================

    if not is_developer:

        # -------------------------------------------------
        # Tell pipeline no more sentences are coming.
        # -------------------------------------------------

        tts_pipeline.finish()

        # -------------------------------------------------
        # Wait until:
        #
        # - remaining TTS is generated
        # - queued audio is played
        # - files are cleaned
        #
        # OR cancellation occurs.
        # -------------------------------------------------

        tts_pipeline.wait()

    # =====================================================
    # Save Conversation
    # =====================================================

    if not answer.strip():

        return

    add_message(
        "assistant",
        answer
    )