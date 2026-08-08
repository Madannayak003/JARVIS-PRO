"""
JARVIS PRO
Developer Memory

Memory Saver Test
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brain.developer.memory.memory_store import (
    MemoryStore,
)

from brain.developer.memory.memory_saver import (
    MemorySaver,
)


def main():

    print("=" * 80)
    print("JARVIS PRO")
    print("Memory Saver Test")
    print("=" * 80)

    with TemporaryDirectory() as temp:

        project_path = Path(temp)

        store = MemoryStore(
            str(project_path),
        )

        saver = MemorySaver(
            store,
        )

        # ------------------------------------------
        # Save complete memory
        # ------------------------------------------

        memory = {

            "version": 1,

            "project": {
                "name": "JARVIS Test",
            },

            "files": {},

            "symbols": {},

            "dependencies": [],

            "style": {},

            "edits": [],

            "session": {},

        }

        success = saver.save(
            memory,
        )

        print("\nSave success:", success)

        assert success is True

        # ------------------------------------------
        # Update
        # ------------------------------------------

        updated = saver.update(
            "project",
            {
                "name": "JARVIS PRO",
            },
        )

        print("Update success:", updated)

        assert updated is True

        # ------------------------------------------
        # Verify
        # ------------------------------------------

        loaded = store.load()

        print("\nLoaded memory:")
        print(loaded)

        assert (
            loaded["project"]["name"]
            == "JARVIS PRO"
        )

    print()
    print("=" * 80)
    print("MEMORY SAVER TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":

    main()