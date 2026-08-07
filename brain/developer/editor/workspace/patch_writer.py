"""
JARVIS PRO
Developer Editor

Patch Applier
"""

from pathlib import Path

from brain.developer.editor.models.patch import (
    Patch,
)

from brain.developer.editor.workspace.appliers.python_applier import (
    PythonApplier,
)

from brain.developer.editor.workspace.appliers.text_applier import (
    TextApplier,
)


class PatchApplier:
    """
    Dispatches patches to the correct language-specific
    patch applier.
    """

    def __init__(self):

        self.python = PythonApplier()

        self.text = TextApplier()

    # --------------------------------------------------

    def apply(
        self,
        project_path: str,
        patch: Patch,
    ) -> str:

        root = Path(project_path)

        target = root / patch.path

        original = ""

        if target.exists():

            original = target.read_text(

                encoding="utf-8",

            )

        extension = target.suffix.lower()

        # ------------------------------------------
        # Python
        # ------------------------------------------

        if extension == ".py":

            return self.python.apply(

                original,

                patch.content,

            )

        # ------------------------------------------
        # Default
        # ------------------------------------------

        return self.text.apply(

            original,

            patch.content,

        )