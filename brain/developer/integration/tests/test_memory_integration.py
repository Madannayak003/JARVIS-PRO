"""
JARVIS PRO
Developer Integration

Phase 10.4
Developer -> Editor -> Memory
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brain.brain_router import (
    BrainRouter,
)


def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("Developer Memory Integration Test")
    print("=" * 90)

    with TemporaryDirectory() as temp:

        project_path = Path(temp)

        # ----------------------------------------------
        # Temporary project
        # ----------------------------------------------

        source = project_path / "main.py"

        source.write_text(
            "def addition(a, b):\n"
            "    return a + b\n",
            encoding="utf-8",
        )

        print("\n[1] Temporary project")
        print(project_path)
        print("PASS")

        # ----------------------------------------------
        # Router
        # ----------------------------------------------

        router = BrainRouter()

        print("\n[2] BrainRouter created")
        print("PASS")

        # ----------------------------------------------
        # Active project
        # ----------------------------------------------

        memory = router.project_resolver.memory

        memory.configure(
            str(project_path),
        )

        memory.load()

        memory.update_session(
            "project_path",
            str(project_path),
        )

        memory.save()

        print("\n[3] Active project configured")
        print("PASS")

        # ----------------------------------------------
        # Controlled generator
        # ----------------------------------------------

        def fake_generate(prompt):

            return (
                "# FILE: main.py\n"
                "```python\n"
                "def addition(a, b):\n"
                "    return a + b\n"
                "\n"
                "def subtract(a, b):\n"
                "    return a - b\n"
                "```\n"
            )

        router.developer.editor.provider.generate = (
            fake_generate
        )

        print("\n[4] Controlled generator installed")
        print("PASS")

        # ----------------------------------------------
        # Execute Developer request
        # ----------------------------------------------

        result = router.route(
            "add subtract function",
        )

        print("\n[5] Developer execution")
        print(result)

        assert result.handled is True

        assert result.result is not None

        assert result.result.success is True

        print("PASS")

        # ----------------------------------------------
        # Memory
        # ----------------------------------------------

        developer_memory = (
            router.developer.memory
        )

        stored = developer_memory.memory

        print("\n[6] Developer memory")
        print(stored)

        assert stored["session"]["project_path"]

        assert len(
            stored["edits"]
        ) == 1

        edit = stored["edits"][0]

        assert (
            edit["request"]
            == "add subtract function"
        )

        assert (
            "main.py"
            in edit["files"]
        )

        assert edit["success"] is True

        print("PASS")

        # ----------------------------------------------
        # Persistence
        # ----------------------------------------------

        reloaded = type(
            developer_memory
        )(
            str(project_path),
        )

        reloaded.load()

        print("\n[7] Reloaded memory")
        print(reloaded.memory)

        assert len(
            reloaded.memory["edits"]
        ) == 1

        assert (
            reloaded.memory["edits"][0]["success"]
            is True
        )

        print("PASS")

    print()
    print("=" * 90)
    print("PHASE 10.4 MEMORY INTEGRATION TEST PASSED")
    print("=" * 90)


if __name__ == "__main__":
    main()