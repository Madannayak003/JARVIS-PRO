"""
JARVIS PRO
Developer Editor

Backup Builder Test
"""

from brain.developer.editor.workspace.backup_builder import (
    BackupBuilder,
)


def main():

    builder = BackupBuilder()

    project = "workspace/Python/PythonCalculator"

    backup = builder.backup(

        project,

        "src/main.py",

    )

    print("=" * 80)
    print("BACKUP CREATED")
    print("=" * 80)
    print(backup)


if __name__ == "__main__":

    main()