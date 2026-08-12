"""
JARVIS PRO
HUD State

Stores the latest state that the visual HUD will display.

This module does not create any UI.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class HUDState:

    status: str = "idle"

    voice_mode: str = "online"

    ai_model: str = ""

    current_task: str = ""

    task_status: str = ""

    listening: bool = False

    speaking: bool = False

    thinking: bool = False

    executing: bool = False

    system: Dict[str, Any] = field(
        default_factory=dict
    )

    notification: str = ""

    error: str = ""

    last_event: str = ""

    last_update: str = ""