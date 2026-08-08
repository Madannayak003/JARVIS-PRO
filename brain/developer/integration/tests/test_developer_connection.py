"""
JARVIS PRO
Developer Integration

Phase 10.3
BrainRouter -> Developer -> Editor

Safe temporary-project integration test.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brain.brain_router import BrainRouter


def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("Developer Connection Integration Test")
    print("=" * 90)

    with TemporaryDirectory() as temp:

        project_path = Path(temp)

        # --------------------------------------------------
        # Create temporary project
        # --------------------------------------------------

        source = project_path / "main.py"

        source.write_text(
            "def addition(a, b):\n"
            "    return a + b\n",
            encoding="utf-8",
        )

        print("\n[1] Temporary project created")
        print(project_path)
        print("PASS")

        # --------------------------------------------------
        # Create router
        # --------------------------------------------------

        router = BrainRouter()

        print("\n[2] BrainRouter created")
        print("PASS")

        # --------------------------------------------------
        # Configure active project memory
        # --------------------------------------------------

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
        print(
            memory.memory.get(
                "session",
                {},
            )
        )
        print("PASS")

        # --------------------------------------------------
        # Verify resolver
        # --------------------------------------------------

        resolved = router.project_resolver.resolve()

        print("\n[4] Active project resolved")
        print(resolved)

        assert resolved is not None

        assert (
            Path(resolved).resolve()
            == project_path.resolve()
        )

        print("PASS")

        # --------------------------------------------------
        # Replace real Ollama provider
        # --------------------------------------------------
        #
        # IMPORTANT:
        # Do NOT call the real model during this test.
        #
        # --------------------------------------------------

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

        print("\n[5] Test generator installed")
        print("PASS")

        # --------------------------------------------------
        # Route Developer request
        # --------------------------------------------------

        result = router.route(
            "add subtract function",
        )

        print("\n[6] BrainRouter result")
        print(result)

        assert result.handled is True

        assert result.module == "developer"

        assert result.result is not None

        print("PASS")

        # --------------------------------------------------
        # Verify file
        # --------------------------------------------------

        updated = source.read_text(
            encoding="utf-8",
        )

        print("\n[7] Updated main.py")
        print("-" * 60)
        print(updated)
        print("-" * 60)

        assert "def addition(a, b):" in updated

        assert "def subtract(a, b):" in updated

        print("PASS")

        # --------------------------------------------------
        # Verify original code remains
        # --------------------------------------------------

        assert (
            "return a + b"
            in updated
        )

        print("\n[8] Existing code preserved")
        print("PASS")

    print()
    print("=" * 90)
    print("PHASE 10.3 DEVELOPER CONNECTION TEST PASSED")
    print("=" * 90)


if __name__ == "__main__":
    main()