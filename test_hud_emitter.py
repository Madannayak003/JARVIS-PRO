"""
JARVIS PRO
HUD Emitter Test

Standalone test.
Does NOT connect to JARVIS runtime.
"""

import time

from hud.emitter import HUDEmitter
from hud.event_contract import HUDEvent


def main():

    print()
    print("=== HUD EMITTER TEST ===")
    print()

    HUDEmitter.emit(
        HUDEvent.IDLE
    )

    time.sleep(1)

    HUDEmitter.emit(
        HUDEvent.LISTENING
    )

    time.sleep(2)

    HUDEmitter.emit(
        HUDEvent.THINKING
    )

    time.sleep(2)

    HUDEmitter.emit(
        HUDEvent.AI_MODEL_CHANGED,
        {
            "provider": "ollama",
            "model": "jarvis"
        }
    )

    time.sleep(2)

    HUDEmitter.emit(
        HUDEvent.TASK_STARTED,
        {
            "task": "Developer Generator"
        }
    )

    time.sleep(2)

    HUDEmitter.emit(
        HUDEvent.EXECUTING,
        {
            "task": "Developer Generator"
        }
    )

    time.sleep(3)

    HUDEmitter.emit(
        HUDEvent.SYSTEM_UPDATE,
        {
            "cpu": 25,
            "ram": 48,
            "battery": 87
        }
    )

    time.sleep(2)

    HUDEmitter.emit(
        HUDEvent.SPEAKING
    )

    time.sleep(2)

    HUDEmitter.emit(
        HUDEvent.TASK_FINISHED,
        {
            "task": "Developer Generator"
        }
    )

    time.sleep(2)

    HUDEmitter.emit(
        HUDEvent.NOTIFICATION,
        {
            "message": "HUD emitter test completed."
        }
    )

    time.sleep(3)

    HUDEmitter.emit(
        HUDEvent.IDLE
    )

    print()
    print("=== HUD EMITTER TEST COMPLETE ===")
    print()


if __name__ == "__main__":
    main()