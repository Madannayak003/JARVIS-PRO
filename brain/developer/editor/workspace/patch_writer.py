"""
JARVIS PRO
Developer Editor

Patch Writer
"""

from pathlib import Path

from brain.developer.editor.models.patch import (
    Patch,
)

from brain.developer.editor.workspace.backup_builder import (
    BackupBuilder,
)

from brain.developer.editor.workspace.patch_applier import (
    PatchApplier,
)


class PatchWriter:
    """
    Applies validated patches to the project.
    """

    def __init__(self):

        self.backup_builder = BackupBuilder()

        self.applier = PatchApplier()

    # --------------------------------------------------

    def write(
        self,
        project_path: str,
        patches: list[Patch],
    ) -> list[str]:

        written = []

        root = Path(project_path)

        for patch in patches:

            destination = root / patch.path

            # --------------------------------------
            # Create folders automatically
            # --------------------------------------

            destination.parent.mkdir(

                parents=True,

                exist_ok=True,

            )

            # --------------------------------------
            # Backup original file
            # --------------------------------------

            self.backup_builder.backup(

                project_path,

                patch.path,

            )

            # --------------------------------------
            # Apply patch
            # --------------------------------------

            content = self.applier.apply(

                project_path,

                patch,

            )

            # --------------------------------------
            # Write merged content
            # --------------------------------------

            destination.write_text(

                content,

                encoding="utf-8",

            )

            written.append(

                str(

                    destination.relative_to(root)

                ).replace("\\", "/")

            )

        return written