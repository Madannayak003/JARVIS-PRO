"""
Compatibility wrapper.

Old dispatcher still imports this file.

Internally it now uses the new
Brain Intent Engine.
"""

from brain.intent_engine import IntentEngine

_engine = IntentEngine()


def detect(command):

    result = _engine.detect(command)

    if result.mode == "planner":
        return "action"

    return "chat"