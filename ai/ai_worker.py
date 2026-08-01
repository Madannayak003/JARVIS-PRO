import time
import re
import threading

from ai.chat import ask_chat
from ai.memory_manager import learn
from voice.manager import speak
from core.context import add_message

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
    
    session = ask_chat(question, stop_event)

    stream = session.stream
    
    is_developer = session.is_developer
    
    print("Request sent:", time.perf_counter() - t0)

    answer = ""

    sentence_buffer = ""

    speaker_threads = []

    # Developer mode should never stream TTS
    
    developer_answer = ""
    
    try:
        
        first = True

        for data in stream:

            if stop_event.is_set():
                
                if first:
                    print("First token:", time.perf_counter() - t0)
                    first = False

                print("\n[AI WORKER] Interrupted")

                return

            token = data.get("response", "")

            if not token:
                continue

            print(token, end="", flush=True)

            answer += token

            # ----------------------------------------
            # Developer Mode
            # ----------------------------------------

            if is_developer:

                developer_answer += token

                continue

            # ----------------------------------------
            # Normal Chat
            # ----------------------------------------

            sentence_buffer += token

            # ----------------------------------------
            # Speak completed sentences immediately
            # ----------------------------------------

            matches = re.findall(

                r'[^.!?]+[.!?]+',

                sentence_buffer

            )

            if matches:

                spoken = "".join(matches)

                sentence_buffer = sentence_buffer[len(spoken):]

                for sentence in matches:

                    sentence = sentence.strip()

                    if sentence:

                        t = threading.Thread(

                            target=speak,

                            args=(sentence,),

                            daemon=True

                        )

                        t.start()

                        speaker_threads.append(t)

    finally:

        print()

    # ----------------------------
    # Don't speak if interrupted
    # ----------------------------

    if stop_event.is_set():

        print("[CHAT] Cancelled before TTS")

        return
    
    # ----------------------------------------
    # Speak remaining text
    # ----------------------------------------

    remaining = sentence_buffer.strip()

    if remaining:

        t = threading.Thread(

            target=speak,

            args=(remaining,),

            daemon=True

        )

        t.start()

        speaker_threads.append(t)

    # ----------------------------------------
    # Wait for speech threads
    # ----------------------------------------

    for t in speaker_threads:

        t.join()

    if not answer.strip():

        return

    add_message("assistant", answer)