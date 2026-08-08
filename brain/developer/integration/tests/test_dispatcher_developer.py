"""
JARVIS PRO
Developer Integration

Phase 10.5
Dispatcher -> BrainRouter -> Developer Result
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import core.dispatcher as dispatcher

from voice.manager import wait_for_speech

def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("Dispatcher Developer Result Test")
    print("=" * 90)

    with TemporaryDirectory() as temp:

        project_path = Path(temp)

        source = project_path / "main.py"

        source.write_text(
            "def addition(a, b):\n"
            "    return a + b\n",
            encoding="utf-8",
        )

        print("\n[1] Temporary project created")
        print("PASS")

        # ------------------------------------------
        # Configure existing BrainRouter
        # ------------------------------------------

        router = dispatcher.brain_router

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

        print("\n[2] Active project configured")
        print("PASS")

        # ------------------------------------------
        # Controlled generator
        # ------------------------------------------

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

        print("\n[3] Controlled generator installed")
        print("PASS")

        # ------------------------------------------
        # Dispatch
        # ------------------------------------------

        dispatcher.dispatch(
            "add subtract function"
        )

        print("\n[4] Dispatcher completed")
        print("PASS")

        # ------------------------------------------
        # Verify file
        # ------------------------------------------

        updated = source.read_text(
            encoding="utf-8",
        )

        assert (
            "def addition(a, b):"
            in updated
        )

        assert (
            "def subtract(a, b):"
            in updated
        )

        print("\n[5] File modified")
        print(updated)
        print("PASS")

        # ------------------------------------------
        # Verify memory
        # ------------------------------------------

        stored = (
            router.developer.memory.memory
        )

        assert len(
            stored["edits"]
        ) == 1

        assert (
            stored["edits"][0]["success"]
            is True
        )

        print("\n[6] Developer memory updated")
        print(
            stored["edits"][0]
        )
        print("PASS")
        
        
        wait_for_speech()

    print()
    print("=" * 90)
    print("PHASE 10.5 DISPATCHER INTEGRATION TEST PASSED")
    print("=" * 90)


if __name__ == "__main__":
    main()