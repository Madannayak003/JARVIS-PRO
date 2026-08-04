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

    edit_type: str = ""

    project_path: str = ""

    target_files: list[str] = field(
        default_factory=list,
    )

    file_contents: dict[str, str] = field(
        default_factory=dict,
    )

    instructions: list[str] = field(
        default_factory=list,
    )