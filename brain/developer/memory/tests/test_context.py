"""
JARVIS PRO
Developer Memory

Memory Context Test
"""

from brain.developer.memory.memory_indexer import (
    MemoryIndexer,
)

from brain.developer.memory.memory_search import (
    MemorySearch,
)

from brain.developer.memory.memory_context import (
    MemoryContext,
)


def main():

    print("=" * 80)
    print("JARVIS PRO")
    print("Memory Context Test")
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

        "edits": [
            {
                "request": "Rename add to addition",
                "success": True,
            },
        ],

        "session": {
            "current_file": "main.py",
        },

    }

    # ------------------------------------------
    # Build search index
    # ------------------------------------------

    indexer = MemoryIndexer()

    indexer.build(
        memory,
    )

    search = MemorySearch(
        indexer,
    )

    # ------------------------------------------
    # Build context
    # ------------------------------------------

    context_builder = MemoryContext(
        search,
    )

    context = context_builder.build(
        query="addition",
        memory=memory,
    )

    print("\nCONTEXT:")
    print(context)

    # ------------------------------------------
    # Verify
    # ------------------------------------------

    assert (
        context["project"]["name"]
        == "JARVIS PRO"
    )

    assert (
        context["style"]["indentation"]
        == 4
    )

    assert (
        context["session"]["current_file"]
        == "main.py"
    )

    assert len(
        context["edits"]
    ) == 1

    assert len(
        context["matches"]
    ) > 0

    # ------------------------------------------
    # Summary
    # ------------------------------------------

    summary = context_builder.summary(
        context,
    )

    print("\nSUMMARY:")
    print(summary)

    assert "Project:" in summary
    assert "Style:" in summary
    assert "Session:" in summary

    print()
    print("=" * 80)
    print("MEMORY CONTEXT TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":

    main()