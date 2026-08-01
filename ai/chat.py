from ai.ollama import ask_ollama_stream
from ai.chat_prompt import CHAT_PROMPT

from brain import pipeline

from dataclasses import dataclass
from typing import Optional, Iterator


# ==========================================================
# Chat Session
# ==========================================================

@dataclass
class ChatSession:

    stream: Iterator

    is_developer: bool = False

    language: Optional[str] = None

    framework: Optional[str] = None

    project_type: Optional[str] = None


# ==========================================================
# AI Chat Entry
# ==========================================================

def ask_chat(question, stop_event=None):

    stream = pipeline.process_stream(

        user_input=question,

        stream_callback=ask_ollama_stream,

        system_prompt=CHAT_PROMPT,

        stop_event=stop_event

    )

    return ChatSession(

        stream=stream,

        is_developer=False,

        language=None,

        framework=None,

        project_type=None

    )