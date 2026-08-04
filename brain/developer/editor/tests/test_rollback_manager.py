"""
JARVIS PRO
Developer Editor

Rollback Manager Test
"""

from pathlib import Path

from brain.developer.editor.workspace.rollback_manager import (
    RollbackManager,
)


def main():

    project = "workspace/Python/PythonCalculator"

    backup_folder = Path(project) / ".jarvis_backups"

    backups = sorted(

        backup_folder.glob("*"),

        reverse=True,

    )

    if not backups:

        print("No backups found.")

        return

    latest = backups[0]

    manager = RollbackManager()

    success = manager.restore(

        project,

        str(

            latest.relative_to(project)

        ).replace("\\", "/"),

        "src/main.py",

    )

    print("=" * 80)

    print("ROLLBACK RESULT")

    print("=" * 80)

    print("Success :", success)

    print("Backup  :", latest.name)


if __name__ == "__main__":

    main()