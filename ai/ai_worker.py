import time
import re
import threading
import queue

from ai.chat import ask_chat
from ai.memory_manager import learn
from voice.manager import speak
from core.context import add_message


# =========================================================
# Voice Text Cleaner
# =========================================================

def clean_for_speech(text):
    """
    Clean AI response for TTS only.

    The original AI response remains unchanged for:
    - chat history
    - screen context
    - memory
    - UI/logs
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

    text = text.replace("```", "")

    # -----------------------------------------------------
    # Remove Markdown bold / italic
    # -----------------------------------------------------

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    text = re.sub(
        r"__(.*?)__",
        r"\1",
        text
    )

    text = re.sub(
        r"(?<!\*)\*(?!\s)(.*?)(?<!\s)\*(?!\*)",
        r"\1",
        text
    )

    text = re.sub(
        r"(?<!_)_(?!\s)(.*?)(?<!\s)_(?!_)",
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
    # Remove numbered Markdown list markers
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
# Speech Queue Worker
# =========================================================

def _speech_worker(
    speech_queue,
    stop_event,
):
    """
    Speaks sentences sequentially.

    Only one sentence is sent to TTS at a time.
    """

    while True:

        if stop_event.is_set():
            return

        try:

            sentence = speech_queue.get(
                timeout=0.05
            )

        except queue.Empty:

            continue

        if sentence is None:

            speech_queue.task_done()

            return

        # -------------------------------------------------
        # Stop before speaking
        # -------------------------------------------------

        if stop_event.is_set():

            speech_queue.task_done()

            return

        sentence = clean_for_speech(
            sentence
        )

        if not sentence:

            speech_queue.task_done()

            continue

        try:

            # wait=True ensures sentences are spoken
            # one after another.
            speak(
                sentence,
                wait=True
            )

        except Exception as e:

            print(
                "[AI WORKER] Speech error:",
                e
            )

        finally:

            speech_queue.task_done()


# =========================================================
# Run Chat
# =========================================================

def run_chat(question, stop_event):

    print("[AI WORKER] Thinking...")
    # ---------------------------------------
    # Learn New Memory
    # ---------------------------------------

    memory_result = learn(question)

    if memory_result["saved"]:

        print(
            f"[MEMORY] Saved -> "
            f"{memory_result['key']} = "
            f"{memory_result['value']}"
        )

    elif memory_result.get("already_known"):

        print(
            "[MEMORY] Already known."
        )

    t0 = time.perf_counter()

    session = ask_chat(
        question,
        stop_event
    )

    stream = session.stream
    is_developer = session.is_developer

    print(
        "Request sent:",
        time.perf_counter() - t0
    )

    answer = ""
    sentence_buffer = ""

    # -----------------------------------------------------
    # One speech queue for this response
    # -----------------------------------------------------

    speech_queue = queue.Queue()

    speech_thread = None

    if not is_developer:

        speech_thread = threading.Thread(
            target=_speech_worker,
            args=(
                speech_queue,
                stop_event,
            ),
            daemon=True,
            name="JARVIS-SpeechWorker",
        )

        speech_thread.start()

    # -----------------------------------------------------
    # Developer Mode
    # -----------------------------------------------------

    developer_answer = ""

    try:

        first = True

        for data in stream:

            if stop_event.is_set():

                if first:

                    print(
                        "First token:",
                        time.perf_counter() - t0
                    )

                    first = False

                print(
                    "\n[AI WORKER] Interrupted"
                )

                return

            token = data.get(
                "response",
                ""
            )

            if not token:

                continue

            print(
                token,
                end="",
                flush=True
            )

            answer += token

            # --------------------------------------------
            # Developer Mode
            # --------------------------------------------

            if is_developer:

                developer_answer += token

                continue

            # --------------------------------------------
            # Normal Chat
            # --------------------------------------------

            sentence_buffer += token

            # --------------------------------------------
            # Sentence extraction
            #
            # Important:
            #
            # Don't split decimal numbers such as:
            #
            # 1084.80
            # 2.44%
            #
            # --------------------------------------------

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

                sentence = match.group(
                    0
                ).strip()

                remaining_start = (
                    match.end()
                )

                sentence_buffer = (
                    sentence_buffer[
                        remaining_start:
                    ]
                )

                if sentence:

                    speech_queue.put(
                        sentence
                    )

    finally:

        print()

    # -----------------------------------------------------
    # Don't speak if interrupted
    # -----------------------------------------------------

    if stop_event.is_set():

        print(
            "[CHAT] Cancelled before TTS"
        )

        return

    # -----------------------------------------------------
    # Speak remaining text
    # -----------------------------------------------------

    remaining = (
        sentence_buffer.strip()
    )

    if remaining and not is_developer:

        speech_queue.put(
            remaining
        )

    # -----------------------------------------------------
    # Finish speech queue
    # -----------------------------------------------------

    if not is_developer:

        speech_queue.put(None)

        if speech_thread:

            speech_thread.join()

    # -----------------------------------------------------
    # Save conversation
    # -----------------------------------------------------

    if not answer.strip():

        return

    add_message(
        "assistant",
        answer
    )