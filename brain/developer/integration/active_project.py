"""
JARVIS PRO
Developer

Active Project Resolver

Phase 10.1
"""

from pathlib import Path

from brain.developer.memory.developer_memory import (
    DeveloperMemory,
)


class ActiveProjectResolver:
    """
    Resolves the currently active Developer project.

    Project information is read from Developer Memory.
    """

    def __init__(
        self,
        memory: DeveloperMemory | None = None,
    ):

        self.memory = memory or DeveloperMemory()

    # ==================================================
    # Configure
    # ==================================================

    def configure(
        self,
        project_path: str,
    ) -> bool:
        """
        Configure the active Developer project.
        """

        if not project_path:

            return False

        path = Path(
            project_path,
        ).expanduser().resolve()

        if not path.exists():

            return False

        if not path.is_dir():

            return False

        self.memory.configure(
            str(path),
        )

        self.memory.update_session(
            "project_path",
            str(path),
        )

        self.memory.save()

        return True

    # ==================================================
    # Resolve
    # ==================================================

    def resolve(self) -> str | None:
        """
        Return the active project path.

        Priority:

        1. Session project_path
        2. Project path stored in project memory
        """

        memory = self.memory.memory

        # ----------------------------------------------
        # Session
        # ----------------------------------------------

        session = memory.get(
            "session",
            {},
        )

        project_path = session.get(
            "project_path",
        )

        if project_path:

            path = Path(
                project_path,
            )

            if path.exists() and path.is_dir():

                return str(
                    path.resolve(),
                )

        # ----------------------------------------------
        # Project memory
        # ----------------------------------------------

        project = memory.get(
            "project",
            {},
        )

        project_path = project.get(
            "path",
        )

        if project_path:

            path = Path(
                project_path,
            )

            if path.exists() and path.is_dir():

                return str(
                    path.resolve(),
                )

        return None