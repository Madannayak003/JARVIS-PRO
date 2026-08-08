"""
JARVIS PRO
Developer Memory

Memory Builder Test
"""

from brain.developer.memory.memory_builder import (
    MemoryBuilder,
)


def main():

    print("=" * 80)
    print("JARVIS PRO")
    print("Memory Builder Test")
    print("=" * 80)

    builder = MemoryBuilder()

    # ------------------------------------------
    # Build
    # ------------------------------------------

    memory = builder.build(
        project={
            "name": "JARVIS PRO",
        },
    )

    print("\nInitial memory:")
    print(memory)

    assert memory["version"] == 1
    assert memory["project"]["name"] == "JARVIS PRO"

    # ------------------------------------------
    # Project
    # ------------------------------------------

    builder.add_project(
        memory,
        "language",
        "Python",
    )

    assert (
        memory["project"]["language"]
        == "Python"
    )

    # ------------------------------------------
    # File
    # ------------------------------------------

    builder.add_file(
        memory,
        "main.py",
        {
            "language": "python",
        },
    )

    assert "main.py" in memory["files"]

    # ------------------------------------------
    # Symbol
    # ------------------------------------------

    builder.add_symbol(
        memory,
        "addition",
        {
            "type": "function",
            "file": "main.py",
        },
    )

    assert "addition" in memory["symbols"]

    # ------------------------------------------
    # Dependency
    # ------------------------------------------

    builder.add_dependency(
        memory,
        {
            "source": "main.py",
            "target": "math",
        },
    )

    assert len(
        memory["dependencies"]
    ) == 1

    # ------------------------------------------
    # Style
    # ------------------------------------------

    builder.update_style(
        memory,
        "indentation",
        4,
    )

    assert (
        memory["style"]["indentation"]
        == 4
    )

    # ------------------------------------------
    # Edit
    # ------------------------------------------

    builder.add_edit(
        memory,
        {
            "request": "Rename add to addition",
            "success": True,
        },
    )

    assert len(
        memory["edits"]
    ) == 1

    # ------------------------------------------
    # Session
    # ------------------------------------------

    builder.update_session(
        memory,
        "current_file",
        "main.py",
    )

    assert (
        memory["session"]["current_file"]
        == "main.py"
    )

    print("\nFinal memory:")
    print(memory)

    print()
    print("=" * 80)
    print("MEMORY BUILDER TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":

    main()