"""
JARVIS PRO
Developer

Public API
"""

from datetime import datetime, timezone

from brain.developer.editor.editor import (
    Editor,
)

from brain.developer.memory.developer_memory import (
    DeveloperMemory,
)

from brain.developer.memory.models.edit_record import (
    EditRecord,
)


class Developer:
    """
    Public entry point for the Developer subsystem.

    Coordinates:

        Developer
            ↓
        Editor
            ↓
        Developer Memory
    """

    def __init__(self):

        self.editor = Editor()

        self.memory = DeveloperMemory()

    # --------------------------------------------------
    # Execute
    # --------------------------------------------------

    def execute(
        self,
        user_request: str,
        project_path: str,
    ):
        """
        Execute a Developer edit and record the result
        in Developer Memory.
        """

        if not user_request:

            return None

        if not project_path:

            return None

        # ----------------------------------------------
        # Configure Developer Memory
        # ----------------------------------------------

        self.memory.configure(
            project_path,
        )

        self.memory.load()

        # ----------------------------------------------
        # Store active project
        # ----------------------------------------------

        self.memory.update_session(
            "project_path",
            project_path,
        )

        # ----------------------------------------------
        # Execute Editor
        # ----------------------------------------------

        result = self.editor.execute(

            user_request,

            project_path,

        )

        # ----------------------------------------------
        # Collect modified files
        # ----------------------------------------------

        files = [

            patch.path

            for patch in result.patches

        ] if result is not None else []

        # ----------------------------------------------
        # Determine edit type
        # ----------------------------------------------

        edit_type = ""

        try:

            edit_type = self.editor.analyzer._detect_action(
                user_request,
            )

        except Exception:

            edit_type = ""

        # ----------------------------------------------
        # Build edit record
        # ----------------------------------------------

        record = EditRecord(

            request=user_request,

            edit_type=edit_type,

            files=files,

            timestamp=datetime.now(
                timezone.utc,
            ).isoformat(),

            success=(
                result.success
                if result is not None
                else False
            ),

            notes=(
                result.message
                if result is not None
                else "Developer execution failed."
            ),

        )

        # ----------------------------------------------
        # Save edit history
        # ----------------------------------------------

        self.memory.add_edit(
            record.__dict__,
        )

        # ----------------------------------------------
        # Save project memory
        # ----------------------------------------------

        self.memory.save()

        return result