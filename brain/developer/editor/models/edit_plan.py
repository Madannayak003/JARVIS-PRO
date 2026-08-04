"""
JARVIS PRO
Developer Editor

Edit Plan
"""

from dataclasses import dataclass, field


@dataclass
class EditPlan:
    """
    Represents the execution plan generated
    by the Edit Planner.
    """

    # -------------------------------------
    # Files
    # -------------------------------------

    primary_files: list[str] = field(
        default_factory=list,
    )

    dependent_files: list[str] = field(
        default_factory=list,
    )

    target_files: list[str] = field(
        default_factory=list,
    )

    # -------------------------------------
    # Execution
    # -------------------------------------

    implementation_steps: list[str] = field(
        default_factory=list,
    )

    validation_steps: list[str] = field(
        default_factory=list,
    )

    # -------------------------------------
    # Metadata
    # -------------------------------------

    estimated_changes: int = 0

    requires_tests: bool = False