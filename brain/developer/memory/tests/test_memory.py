"""
JARVIS PRO
Developer Memory

Final Developer Memory Test
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brain.developer.memory.developer_memory import (
    DeveloperMemory,
)


def main():

    print("=" * 100)
    print("JARVIS PRO")
    print("Developer Memory Final Integration Test")
    print("=" * 100)

    with TemporaryDirectory() as temp:

        project_path = Path(temp)

        # ==================================================
        # 1. Create public memory API
        # ==================================================

        memory = DeveloperMemory(
            str(project_path),
        )

        print("\n[1] DeveloperMemory created")
        print("PASS")

        # ==================================================
        # 2. Load
        # ==================================================

        loaded = memory.load()

        print("\n[2] Initial memory")
        print(loaded)

        assert isinstance(
            loaded,
            dict,
        )

        assert loaded["version"] == 1

        print("PASS")

        # ==================================================
        # 3. Project memory
        # ==================================================

        memory.add_project(
            "name",
            "JARVIS PRO",
        )

        memory.add_project(
            "language",
            "Python",
        )

        print("\n[3] Project memory")
        print(memory.memory["project"])

        assert (
            memory.memory["project"]["name"]
            == "JARVIS PRO"
        )

        assert (
            memory.memory["project"]["language"]
            == "Python"
        )

        print("PASS")

        # ==================================================
        # 4. File memory
        # ==================================================

        memory.add_file(
            "main.py",
            {
                "language": "python",
                "functions": [
                    "addition",
                    "subtract",
                    "multiply",
                    "divide",
                ],
            },
        )

        print("\n[4] File memory")
        print(memory.memory["files"])

        assert "main.py" in memory.memory["files"]

        print("PASS")

        # ==================================================
        # 5. Symbol memory
        # ==================================================

        memory.add_symbol(
            "addition",
            {
                "type": "function",
                "file": "main.py",
            },
        )

        print("\n[5] Symbol memory")
        print(memory.memory["symbols"])

        assert (
            "addition"
            in memory.memory["symbols"]
        )

        print("PASS")

        # ==================================================
        # 6. Dependency memory
        # ==================================================

        memory.add_dependency(
            {
                "source": "main.py",
                "target": "math",
            },
        )

        print("\n[6] Dependency memory")
        print(memory.memory["dependencies"])

        assert len(
            memory.memory["dependencies"]
        ) == 1

        print("PASS")

        # ==================================================
        # 7. Style memory
        # ==================================================

        memory.update_style(
            "indentation",
            4,
        )

        memory.update_style(
            "naming",
            "snake_case",
        )

        print("\n[7] Style memory")
        print(memory.memory["style"])

        assert (
            memory.memory["style"]["indentation"]
            == 4
        )

        assert (
            memory.memory["style"]["naming"]
            == "snake_case"
        )

        print("PASS")

        # ==================================================
        # 8. Edit history
        # ==================================================

        memory.add_edit(
            {
                "request": "Rename add to addition",
                "edit_type": "RENAME",
                "files": [
                    "main.py",
                ],
                "success": True,
            },
        )

        print("\n[8] Edit history")
        print(memory.memory["edits"])

        assert len(
            memory.memory["edits"]
        ) == 1

        print("PASS")

        # ==================================================
        # 9. Session memory
        # ==================================================

        memory.update_session(
            "current_file",
            "main.py",
        )

        memory.update_session(
            "last_action",
            "rename",
        )

        print("\n[9] Session memory")
        print(memory.memory["session"])

        assert (
            memory.memory["session"]["current_file"]
            == "main.py"
        )

        print("PASS")

        # ==================================================
        # 10. Search
        # ==================================================

        results = memory.search(
            "addition",
        )

        print("\n[10] Search results")

        for result in results:
            print(result)

        assert len(results) > 0

        assert any(
            result["key"] == "addition"
            for result in results
        )

        print("PASS")

        # ==================================================
        # 11. Context
        # ==================================================

        context = memory.get_context(
            "addition",
        )

        print("\n[11] Memory context")
        print(context)

        assert (
            context["project"]["name"]
            == "JARVIS PRO"
        )

        assert len(
            context["matches"]
        ) > 0

        print("PASS")

        # ==================================================
        # 12. Save
        # ==================================================

        saved = memory.save()

        print("\n[12] Save")
        print("Success:", saved)

        assert saved is True

        print("PASS")

        # ==================================================
        # 13. Verify persistent file
        # ==================================================

        memory_file = (
            project_path
            / ".jarvis_memory"
            / "memory.json"
        )

        print("\n[13] Persistent memory file")
        print(memory_file)

        assert memory_file.exists()

        print("PASS")

        # ==================================================
        # 14. Create second instance
        # ==================================================

        memory2 = DeveloperMemory(
            str(project_path),
        )

        reloaded = memory2.load()

        print("\n[14] Reloaded memory")
        print(reloaded)

        assert (
            reloaded["project"]["name"]
            == "JARVIS PRO"
        )

        assert (
            reloaded["project"]["language"]
            == "Python"
        )

        assert "main.py" in (
            reloaded["files"]
        )

        assert "addition" in (
            reloaded["symbols"]
        )

        assert len(
            reloaded["dependencies"]
        ) == 1

        assert len(
            reloaded["edits"]
        ) == 1

        print("PASS")

        # ==================================================
        # 15. Search after reload
        # ==================================================

        results2 = memory2.search(
            "addition",
        )

        print("\n[15] Search after reload")

        for result in results2:
            print(result)

        assert len(results2) > 0

        print("PASS")

        # ==================================================
        # Final memory
        # ==================================================

        print("\n" + "=" * 100)
        print("FINAL MEMORY")
        print("=" * 100)

        print(memory2.memory)

    # ==================================================
    # Final result
    # ==================================================

    print()
    print("#" * 100)
    print("PHASE 9 MEMORY FINAL INTEGRATION TEST PASSED")
    print("#" * 100)


if __name__ == "__main__":
    main()