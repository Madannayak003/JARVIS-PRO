"""
JARVIS PRO
Developer Memory

Memory Indexer Test
"""

from brain.developer.memory.memory_indexer import (
    MemoryIndexer,
)


def main():

    print("=" * 80)
    print("JARVIS PRO")
    print("Memory Indexer Test")
    print("=" * 80)

    memory = {

        "version": 1,

        "project": {
            "name": "JARVIS PRO",
            "language": "Python",
        },

        "files": {
            "main.py": {
                "language": "python",
            },
        },

        "symbols": {
            "addition": {
                "type": "function",
                "file": "main.py",
            },
        },

        "dependencies": [
            {
                "source": "main.py",
                "target": "math",
            },
        ],

        "style": {
            "indentation": 4,
        },

        "edits": [],

        "session": {},
    }

    indexer = MemoryIndexer()

    index = indexer.build(
        memory,
    )

    print("\nINDEX:")
    print(index)

    # ------------------------------------------
    # Verify categories
    # ------------------------------------------

    assert "project" in index
    assert "files" in index
    assert "symbols" in index
    assert "dependencies" in index
    assert "style" in index

    # ------------------------------------------
    # Verify lookup
    # ------------------------------------------

    project = indexer.get(
        "project",
        "name",
    )

    print("\nProject name:", project)

    assert project == "JARVIS PRO"

    # ------------------------------------------
    # Verify category
    # ------------------------------------------

    files = indexer.get_category(
        "files",
    )

    print("\nFiles:", files)

    assert "main.py" in files

    # ------------------------------------------
    # Verify update
    # ------------------------------------------

    indexer.update(
        "project",
        "framework",
        "Ollama",
    )

    assert (
        indexer.get(
            "project",
            "framework",
        )
        == "Ollama"
    )

    print("\nUpdate: PASS")

    # ------------------------------------------
    # Verify clear
    # ------------------------------------------

    indexer.clear()

    assert indexer.index == {}

    print("Clear: PASS")

    print()
    print("=" * 80)
    print("MEMORY INDEXER TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":

    main()