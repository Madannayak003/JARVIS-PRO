"""
JARVIS PRO HUD
Event Definitions
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class HUDEvent:

    name: str

    data: dict[str, Any] = field(
        default_factory=dict
    )

    timestamp: str = field(
        default_factory=lambda:
        datetime.now().isoformat(
            timespec="seconds"
        )
    )

    source: str | None = None


# =========================================================
# Events
# =========================================================

HUD_IDLE = "idle"

HUD_LISTENING = "listening"

HUD_THINKING = "thinking"

HUD_SPEAKING = "speaking"

HUD_EXECUTING = "executing"

HUD_TASK_STARTED = "task_started"

HUD_TASK_FINISHED = "task_finished"

HUD_TASK_FAILED = "task_failed"

HUD_VOICE_MODE_CHANGED = "voice_mode_changed"

HUD_AI_MODEL_CHANGED = "ai_model_changed"

HUD_SYSTEM_UPDATE = "system_update"

HUD_NOTIFICATION = "notification"

HUD_ERROR = "error"

HUD_COMMAND = "command"

HUD_RESPONSE = "response"