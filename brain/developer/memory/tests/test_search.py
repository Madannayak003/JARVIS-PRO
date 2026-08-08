"""
JARVIS PRO
Developer Memory

Memory Search Test
"""

from brain.developer.memory.memory_indexer import (
    MemoryIndexer,
)

from brain.developer.memory.memory_search import (
    MemorySearch,
)


def main():

    print("=" * 80)
    print("JARVIS PRO")
    print("Memory Search Test")
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

            "calculator.py": {
                "language": "python",
            },

        },

        "symbols": {

            "addition": {
                "type": "function",
                "file": "main.py",
            },

            "calculator": {
                "type": "function",
                "file": "calculator.py",
            },

        },

        "style": {

            "naming": "snake_case",

        },

    }

    # ------------------------------------------
    # Build index
    # ------------------------------------------

    indexer = MemoryIndexer()

    indexer.build(
        memory,
    )

    # ------------------------------------------
    # Search
    # ------------------------------------------

    search = MemorySearch(
        indexer,
    )

    results = search.search(
        "calculator python",
    )

    print("\nSEARCH RESULTS")

    for result in results:

        print(
            result
        )

    # ------------------------------------------
    # Verify
    # ------------------------------------------

    assert len(results) > 0

    assert any(

        result["key"] == "calculator"

        for result in results

    )

    # ------------------------------------------
    # Empty search
    # ------------------------------------------

    empty = search.search("")

    assert empty == []

    print("\nEmpty search: PASS")

    # ------------------------------------------
    # Limit
    # ------------------------------------------

    limited = search.search(
        "python",
        limit=1,
    )

    assert len(limited) <= 1

    print("Limit: PASS")

    print()
    print("=" * 80)
    print("MEMORY SEARCH TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":

    main()