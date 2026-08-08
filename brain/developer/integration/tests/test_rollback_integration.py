"""
JARVIS PRO
Developer Integration

Phase 10.6
Patch Writer Error + Rollback Test
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brain.developer.editor.models.patch import (
    Patch,
)

from brain.developer.editor.workspace.patch_writer import (
    PatchWriter,
)


def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("Rollback Integration Test")
    print("=" * 90)

    with TemporaryDirectory() as temp:

        project = Path(temp)

        # ------------------------------------------
        # Original project
        # ------------------------------------------

        source = project / "main.py"

        original = (
            "def addition(a, b):\n"
            "    return a + b\n"
        )

        source.write_text(

            original,

            encoding="utf-8",

        )

        print("\n[1] Original file created")
        print(source.read_text())
        print("PASS")

        # ------------------------------------------
        # Writer
        # ------------------------------------------

        writer = PatchWriter()

        print("\n[2] PatchWriter created")
        print("PASS")

        # ------------------------------------------
        # Force failure AFTER first patch
        # ------------------------------------------

        original_applier = writer.applier.apply

        call_count = 0

        def failing_apply(
            project_path,
            patch,
        ):

            nonlocal call_count

            call_count += 1

            # First patch works
            if call_count == 1:

                return original_applier(
                    project_path,
                    patch,
                )

            # Second patch fails
            raise RuntimeError(
                "Intentional test failure"
            )

        writer.applier.apply = failing_apply

        # ------------------------------------------
        # Two patches
        # ------------------------------------------

        patches = [

            Patch(

                path="main.py",

                language="python",

                content=(
                    "def addition(a, b):\n"
                    "    return a + b + 10\n"
                ),

            ),

            Patch(

                path="second.py",

                language="python",

                content=(
                    "print('second')\n"
                ),

            ),

        ]

        print("\n[3] Failure scenario prepared")
        print("PASS")

        # ------------------------------------------
        # Execute
        # ------------------------------------------

        failed = False

        try:

            writer.write(

                str(project),

                patches,

            )

        except RuntimeError as error:

            failed = True

            print(
                "\n[4] Expected failure:"
            )

            print(error)

        assert failed is True

        print("PASS")

        # ------------------------------------------
        # Verify original restored
        # ------------------------------------------

        restored = source.read_text(

            encoding="utf-8",

        )

        print(
            "\n[5] main.py after rollback"
        )

        print(restored)

        assert restored == original

        print("PASS")

        # ------------------------------------------
        # Verify second file absent
        # ------------------------------------------

        second = project / "second.py"

        assert not second.exists()

        print(
            "\n[6] New file cleanup"
        )

        print(
            "second.py does not exist"
        )

        print("PASS")

        # ------------------------------------------
        # Verify backup exists
        # ------------------------------------------

        backup_root = (

            project / ".jarvis_backups"

        )

        assert backup_root.exists()

        backups = list(

            backup_root.iterdir()

        )

        assert backups

        print(
            "\n[7] Backup created"
        )

        print(
            backups
        )

        print("PASS")

    print()
    print("=" * 90)
    print(
        "PHASE 10.6 ROLLBACK INTEGRATION TEST PASSED"
    )
    print("=" * 90)


if __name__ == "__main__":
    main()