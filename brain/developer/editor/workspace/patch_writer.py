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


class PatchWriter:
    """
    Applies parsed patches to the project.
    """
    
    
    def __init__(self):

        self.backup_builder = BackupBuilder()

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
            # Write file
            # --------------------------------------
            
            
            self.backup_builder.backup(

                project_path,

                patch.path,

            )
            

            destination.write_text(

                patch.content,

                encoding="utf-8",

            )

            written.append(

                str(

                    destination.relative_to(root)

                ).replace("\\", "/")

            )

        return written