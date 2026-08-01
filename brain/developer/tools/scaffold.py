"""
JARVIS PRO
Developer

Scaffold Tool
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


STRUCTURES = {

        "workspace": {

        "folders": [

            "workspace",

            "workspace/builders",

            "workspace/models",

            "workspace/rules",

            "workspace/writers",

        ],

        "files": [

            "workspace/__init__.py",

            "workspace/workspace.py",

            "workspace/builders/__init__.py",
            "workspace/builders/project_builder.py",
            "workspace/builders/folder_builder.py",
            "workspace/builders/file_builder.py",

            "workspace/models/__init__.py",
            "workspace/models/workspace_result.py",
            "workspace/models/created_file.py",
            "workspace/models/created_folder.py",

            "workspace/rules/__init__.py",
            "workspace/rules/workspace_rules.py",

            "workspace/writers/__init__.py",
            "workspace/writers/folder_writer.py",
            "workspace/writers/file_writer.py",

        ]

    },

}


def create_structure(name: str):

    if name not in STRUCTURES:

        print(f"Unknown structure: {name}")

        return

    structure = STRUCTURES[name]

    print(f"\nCreating '{name}'...\n")

    for folder in structure["folders"]:

        path = ROOT / folder

        path.mkdir(parents=True, exist_ok=True)

        print(f"[Folder] {folder}")

    for file in structure["files"]:

        path = ROOT / file

        path.parent.mkdir(parents=True, exist_ok=True)

        path.touch(exist_ok=True)

        print(f"[File]   {file}")

    print("\nDone.")


def main():

    if len(sys.argv) != 2:

        print("\nUsage:")

        print("python -m brain.developer.tools.scaffold prompt_builder")

        return

    create_structure(sys.argv[1])


if __name__ == "__main__":

    main()