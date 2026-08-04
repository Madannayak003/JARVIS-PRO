"""
JARVIS PRO
Developer Editor

Edit Planner
"""

from brain.developer.editor.models import (
    EditRequest,
)

from brain.developer.editor.planner.file_selector import (
    FileSelector,
)


class EditPlanner:
    """
    Plans the editing operation.
    """

    def __init__(self):

        self.selector = FileSelector()

    # --------------------------------------------------

    def plan(
        self,
        request: EditRequest,
    ) -> EditRequest:
        """
        Select the files that should be edited.
        """

        request.target_files = self.selector.select(

            request,

        )

        return request