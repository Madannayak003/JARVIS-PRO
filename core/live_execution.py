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


def is_live_execution() -> bool:
    """
    Return True when JARVIS is currently executing a command
    originating from Gemini Live.
    """

    with _lock:
        return _live_execution_count > 0


@contextmanager
def live_execution():

    global _live_execution_count

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