"""
JARVIS PRO
Developer Memory

Memory Manager Test
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brain.developer.memory.memory_manager import (
    MemoryManager,
)


def main():

    print("=" * 80)
    print("JARVIS PRO")
    print("Memory Manager Test")
    print("=" * 80)

    with TemporaryDirectory() as temp:

        project_path = Path(temp)

        # ------------------------------------------
        # Create Manager
        # ------------------------------------------

        manager = MemoryManager(
            str(project_path),
        )

        print("\n[1] Manager created")

        # ------------------------------------------
        # Load initial memory
        # ------------------------------------------

        memory = manager.load()

        print("[2] Initial memory:")
        print(memory)

        assert isinstance(
            memory,
            dict,
        )

        assert memory["version"] == 1

        # ------------------------------------------
        # Project
        # ------------------------------------------

        manager.add_project(
            "name",
            "JARVIS PRO",
        )

        manager.add_project(
            "language",
            "Python",
        )

        # ------------------------------------------
        # File
        # ------------------------------------------

        manager.add_file(
            "main.py",
            {
                "language": "python",
                "functions": [
                    "addition",
                ],
            },
        )

        # ------------------------------------------
        # Symbol
        # ------------------------------------------

        manager.add_symbol(
            "addition",
            {
                "type": "function",
                "file": "main.py",
            },
        )

        # ------------------------------------------
        # Dependency
        # ------------------------------------------

        manager.add_dependency(
            {
                "source": "main.py",
                "target": "math",
            },
        )

        # ------------------------------------------
        # Style
        # ------------------------------------------

        manager.update_style(
            "indentation",
            4,
        )

        manager.update_style(
            "naming",
            "snake_case",
        )

        # ------------------------------------------
        # Edit
        # ------------------------------------------

        manager.add_edit(
            {
                "request": "Rename add to addition",
                "edit_type": "RENAME",
                "files": [
                    "main.py",
                ],
                "success": True,
            },
        )

        # ------------------------------------------
        # Session
        # ------------------------------------------

        manager.update_session(
            "current_file",
            "main.py",
        )

        # ------------------------------------------
        # Verify memory
        # ------------------------------------------

        print("\n[3] Current memory:")
        print(manager.memory)

        assert (
            manager.memory["project"]["name"]
            == "JARVIS PRO"
        )

        assert (
            manager.memory["project"]["language"]
            == "Python"
        )

        assert "main.py" in (
            manager.memory["files"]
        )

        assert "addition" in (
            manager.memory["symbols"]
        )

        assert len(
            manager.memory["dependencies"]
        ) == 1

        assert (
            manager.memory["style"]["indentation"]
            == 4
        )

        assert len(
            manager.memory["edits"]
        ) == 1

        assert (
            manager.memory["session"]["current_file"]
            == "main.py"
        )

        print("[4] Memory data: PASS")

        # ------------------------------------------
        # Search
        # ------------------------------------------

        results = manager.search(
            "addition",
        )

        print("\n[5] Search results:")

        for result in results:

            print(result)

        assert len(results) > 0

        assert any(

            result["key"] == "addition"

            for result in results

        )

        print("[6] Search: PASS")

        # ------------------------------------------
        # Context
        # ------------------------------------------

        context = manager.get_context(
            "addition",
        )

        print("\n[7] Context:")
        print(context)

        assert (
            context["project"]["name"]
            == "JARVIS PRO"
        )

        assert len(
            context["matches"]
        ) > 0

        print("[8] Context: PASS")

        # ------------------------------------------
        # Save
        # ------------------------------------------

        saved = manager.save()

        print(
            "\n[9] Save success:",
            saved,
        )

        assert saved is True

        # ------------------------------------------
        # Verify persistence
        # ------------------------------------------

        memory_file = (
            project_path
            / ".jarvis_memory"
            / "memory.json"
        )

        print(
            "[10] Memory file exists:",
            memory_file.exists(),
        )

        assert memory_file.exists()

        # ------------------------------------------
        # New Manager
        # ------------------------------------------

        manager2 = MemoryManager(
            str(project_path),
        )

        loaded = manager2.load()

        print("\n[11] Reloaded memory:")
        print(loaded)

        assert (
            loaded["project"]["name"]
            == "JARVIS PRO"
        )

        assert "main.py" in (
            loaded["files"]
        )

        assert "addition" in (
            loaded["symbols"]
        )

        print("[12] Persistence: PASS")

    print()
    print("=" * 80)
    print("MEMORY MANAGER TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":

    main()