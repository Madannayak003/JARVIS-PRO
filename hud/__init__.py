"""
JARVIS PRO
HUD Foundation

Presentation layer only.

The HUD must never control JARVIS core logic.
"""

from .manager import HUDManager, hud
from .adapter import HUDAdapter

__all__ = [
    "HUDManager",
    "HUDAdapter",
    "hud",
]