"""
=============================================================
JARVIS PRO — LIVE EXECUTION CONTEXT
=============================================================

Global execution state used to identify commands originating
from Gemini Live Conversation.

This is intentionally process-wide because Live commands may
cross worker/thread boundaries.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager


_lock = threading.RLock()

_live_execution_count = 0

_live_responses = []


def is_live_execution() -> bool:
    """
    Return True when JARVIS is currently executing a command
    originating from Gemini Live.
    """

    with _lock:
        return _live_execution_count > 0


def capture_live_response(text: str) -> None:
    """
    Capture authoritative JARVIS speech generated while a
    Live command is executing.

    This does NOT speak anything. It only stores the text so
    Gemini Live can receive the real JARVIS skill result.
    """

    if not text:
        return

    with _lock:

        if _live_execution_count <= 0:
            return

        _live_responses.append(str(text))


def get_live_responses() -> list[str]:
    """
    Return all authoritative responses captured during the
    current Live execution context.
    """

    with _lock:
        return list(_live_responses)


def clear_live_responses() -> None:
    """
    Clear previously captured Live responses.
    """

    with _lock:
        _live_responses.clear()


@contextmanager
def live_execution():
    global _live_execution_count

    clear_live_responses()

    with _lock:
        _live_execution_count += 1

    try:
        yield
    finally:
        with _lock:
            _live_execution_count = max(
                0,
                _live_execution_count - 1,
            )