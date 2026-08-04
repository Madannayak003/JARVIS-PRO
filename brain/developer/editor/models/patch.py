"""
JARVIS PRO
Developer Editor

Patch
"""

from dataclasses import dataclass


@dataclass
class Patch:
    """
    Represents a single file modification.
    """

    path: str = ""

    old_content: str = ""

    new_content: str = ""

    changed: bool = False