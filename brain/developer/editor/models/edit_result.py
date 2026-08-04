"""
JARVIS PRO
Developer Editor

Edit Result
"""

from dataclasses import dataclass, field

from brain.developer.editor.models.patch import Patch


@dataclass
class EditResult:
    """
    Final result of an editing operation.
    """

    success: bool = False

    patches: list[Patch] = field(default_factory=list)

    files_modified: int = 0

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)