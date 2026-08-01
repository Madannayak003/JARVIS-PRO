"""
JARVIS PRO
Developer

Scaffold Tool
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


STRUCTURES = {

    "editor": {

        "folders": [

            "editor",

            "editor/analyzer",

            "editor/planner",

            "editor/prompt_builder",

            "editor/provider",

            "editor/parser",

            "editor/validator",

            "editor/workspace",

            "editor/models",

            "editor/rules",

            "editor/tests",

        ],

        "files": [

            # Root
            "editor/__init__.py",
            "editor/editor.py",

            # Analyzer
            "editor/analyzer/__init__.py",
            "editor/analyzer/edit_analyzer.py",
            "editor/analyzer/target_locator.py",

            # Planner
            "editor/planner/__init__.py",
            "editor/planner/edit_planner.py",

            # Prompt Builder
            "editor/prompt_builder/__init__.py",
            "editor/prompt_builder/prompt_builder.py",
            "editor/prompt_builder/system_builder.py",
            "editor/prompt_builder/context_builder.py",
            "editor/prompt_builder/instruction_builder.py",

            # Provider
            "editor/provider/__init__.py",
            "editor/provider/base_provider.py",
            "editor/provider/ollama_provider.py",

            # Parser
            "editor/parser/__init__.py",
            "editor/parser/response_parser.py",
            "editor/parser/patch_parser.py",

            # Validator
            "editor/validator/__init__.py",
            "editor/validator/edit_validator.py",

            # Workspace
            "editor/workspace/__init__.py",
            "editor/workspace/patch_writer.py",
            "editor/workspace/backup_builder.py",
            "editor/workspace/rollback.py",

            # Models
            "editor/models/__init__.py",
            "editor/models/edit_context.py",
            "editor/models/edit_request.py",
            "editor/models/edit_result.py",
            "editor/models/patch.py",

            # Rules
            "editor/rules/__init__.py",
            "editor/rules/edit_rules.py",

            # Tests
            "editor/tests/__init__.py",
            "editor/tests/test_editor.py",

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