"""
JARVIS PRO
Developer Editor

Patch Applier
"""

from pathlib import Path

from brain.developer.editor.models.patch import (
    Patch,
)


class PatchApplier:
    """
    Applies parsed patches to existing files.

    The PatchApplier decides whether to:

    - replace the entire file
    - merge a partial update
    - delegate to a language-specific applier

    Current version:
        Full-file replacement.

    Future versions:
        Python AST merge
        HTML DOM merge
        JSON merge
        C/C++ merge
    """

    # --------------------------------------------------

    def apply(

        self,

        project_path: str,

        patch: Patch,

    ) -> str:

        root = Path(project_path)

        target = root / patch.path

        # ------------------------------------------
        # Existing file
        # ------------------------------------------

        original = ""

        if target.exists():

            original = target.read_text(

                encoding="utf-8",

            )

        # ------------------------------------------
        # Current strategy
        #
        # Phase 8:
        # Return full generated file.
        #
        # Phase 9:
        # Merge snippets.
        # ------------------------------------------

        merged = self._merge(

            original,

            patch.content,

        )

        return merged

    # --------------------------------------------------

    def _merge(

        self,

        original: str,

        generated: str,

    ) -> str:

        generated = generated.strip()

        if not generated:

            return original

        # ------------------------------------------
        # Current implementation
        #
        # If the model generated a complete file,
        # return it.
        #
        # Later this becomes AST-based.
        # ------------------------------------------

        return generated + "\n"