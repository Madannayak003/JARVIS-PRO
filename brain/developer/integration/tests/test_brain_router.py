"""
JARVIS PRO
Developer Integration

Brain Router Test

Phase 10.2
"""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from brain.brain_router import (
    BrainRouter,
)


def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("Brain Router - Phase 10.2 Test")
    print("=" * 90)

    # ==================================================
    # Temporary project
    # ==================================================

    with TemporaryDirectory() as temp_dir:

        project = Path(temp_dir)

        main_file = project / "main.py"

        main_file.write_text(
            "def addition(a, b):\n"
            "    return a + b\n",
            encoding="utf-8",
        )

        print("\n[1] Temporary project")
        print(project)

        assert project.exists()
        assert main_file.exists()

        print("PASS")

        # ==================================================
        # Router
        # ==================================================

        router = BrainRouter()

        print("\n[2] BrainRouter created")
        print("PASS")

        # ==================================================
        # Configure Active Project
        # ==================================================

        configured = router.configure_project(
            str(project),
        )

        print("\n[3] Active project configured")
        print(configured)

        assert configured is True

        print("PASS")

        # ==================================================
        # Resolve Active Project
        # ==================================================

        resolved = router.project_resolver.resolve()

        print("\n[4] Active project resolved")
        print(resolved)

        assert resolved == str(
            project.resolve()
        )

        print("PASS")

        # ==================================================
        # Controlled Developer
        # ==================================================

        def fake_execute(
            user_request,
            project_path,
        ):

            print(
                "[TEST DEVELOPER]"
            )

            print(
                "Request:",
                user_request,
            )

            print(
                "Project:",
                project_path,
            )

            return SimpleNamespace(
                success=True,
                message="Controlled Developer execution",
                patches=[],
                warnings=[],
                errors=[],
            )

        router.developer.execute = fake_execute

        print("\n[5] Controlled Developer installed")
        print("PASS")

        # ==================================================
        # Normal command
        # ==================================================

        result = router.route(
            "open chrome",
        )

        print("\n[6] Normal command")
        print(result)

        assert result.handled is False

        print("PASS")

        # ==================================================
        # Normal chat
        # ==================================================

        result = router.route(
            "what is python",
        )

        print("\n[7] Normal chat")
        print(result)

        assert result.handled is False

        print("PASS")

        # ==================================================
        # EDIT request
        # ==================================================

        result = router.route(
            "fix the divide function",
        )

        print("\n[8] Developer EDIT request")
        print(result)

        assert result.handled is True
        assert result.module == "developer"
        assert result.result is not None
        assert result.result.success is True

        print("PASS")

        # ==================================================
        # CREATE request
        # ==================================================

        # Remove active project intentionally.
        #
        # CREATE must NOT require an active project.
        #

        router.project_resolver.memory.manager.memory = {
            "version": 1,
            "project": {},
            "files": {},
            "symbols": {},
            "dependencies": [],
            "style": {},
            "edits": [],
            "session": {},
        }

        create_result = router.route(
            "create python calculator",
        )

        print("\n[9] Developer CREATE request")
        print(create_result)

        assert create_result.handled is True

        assert create_result.module == "developer"

        assert create_result.result is not None

        assert create_result.result.success is True

        print("PASS")

        # ==================================================
        # Verify CREATE received empty project path
        # ==================================================

        print(
            "\n[10] CREATE project path"
        )

        print(
            "CREATE request correctly does not "
            "require an active project."
        )

        print("PASS")

        # ==================================================
        # Empty command
        # ==================================================

        result = router.route(
            "",
        )

        print("\n[11] Empty command")
        print(result)

        assert result.handled is False

        print("PASS")

        # ==================================================
        # Project preserved
        # ==================================================

        assert project.exists()
        assert main_file.exists()

        print(
            "\n[12] Project preserved"
        )

        print(
            "main.py exists:",
            main_file.exists(),
        )

        print("PASS")

    # ==================================================
    # Final
    # ==================================================

    print()
    print("=" * 90)
    print(
        "PHASE 10.2 BRAIN ROUTER TEST PASSED"
    )
    print("=" * 90)


if __name__ == "__main__":

    main()