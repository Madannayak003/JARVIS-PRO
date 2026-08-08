"""
JARVIS PRO
Developer Integration

Active Project Resolver Test
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brain.developer.memory.developer_memory import (
    DeveloperMemory,
)

from brain.developer.integration.active_project import (
    ActiveProjectResolver,
)


def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("Active Project Resolver Test")
    print("=" * 90)

    with TemporaryDirectory() as temp:

        project_path = Path(temp)

        # ------------------------------------------
        # Create memory
        # ------------------------------------------

        memory = DeveloperMemory(
            str(project_path),
        )

        memory.load()

        print("\n[1] Developer memory created")
        print("PASS")

        # ------------------------------------------
        # Store active project path
        # ------------------------------------------

        memory.update_session(
            "project_path",
            str(project_path),
        )

        memory.save()

        print("\n[2] Project path stored")
        print(
            memory.memory["session"]
        )
        print("PASS")

        # ------------------------------------------
        # Create resolver
        # ------------------------------------------

        resolver = ActiveProjectResolver(
            memory,
        )

        print("\n[3] Resolver created")
        print("PASS")

        # ------------------------------------------
        # Resolve
        # ------------------------------------------

        resolved = resolver.resolve()

        print("\n[4] Resolved project")
        print(resolved)

        assert resolved is not None

        assert (
            Path(resolved).resolve()
            == project_path.resolve()
        )

        print("PASS")

        # ------------------------------------------
        # Verify persistence
        # ------------------------------------------

        memory2 = DeveloperMemory(
            str(project_path),
        )

        memory2.load()

        resolver2 = ActiveProjectResolver(
            memory2,
        )

        resolved2 = resolver2.resolve()

        print("\n[5] Resolved after reload")
        print(resolved2)

        assert resolved2 is not None

        assert (
            Path(resolved2).resolve()
            == project_path.resolve()
        )

        print("PASS")

    print()
    print("=" * 90)
    print("ACTIVE PROJECT RESOLVER TEST PASSED")
    print("=" * 90)


if __name__ == "__main__":
    main()