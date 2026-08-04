"""
JARVIS PRO
Developer Editor

Patch Writer Test
"""

from brain.developer.editor.models.patch import Patch

from brain.developer.editor.workspace.patch_writer import (
    PatchWriter,
)


def main():

    project = "workspace/Python/PythonCalculator"

    patches = [

        Patch(

            path="src/main.py",

            language="python",

            content="""print("PATCH WRITER WORKING")""",

        ),

    ]

    writer = PatchWriter()

    written = writer.write(

        project,

        patches,

    )

    print("=" * 80)

    print("FILES WRITTEN")

    print("=" * 80)

    for file in written:

        print(file)


if __name__ == "__main__":

    main()