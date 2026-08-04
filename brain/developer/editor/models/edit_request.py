"""
JARVIS PRO
Developer Editor

Edit Request
"""

from dataclasses import dataclass, field


@dataclass
class EditRequest:
    """
    Represents a user's edit request.
    """

    user_request: str = ""

    target_files: list[str] = field(default_factory=list)

    instructions: list[str] = field(default_factory=list)

    edit_type: str = ""

    project_path: str = ""