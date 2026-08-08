"""
JARVIS PRO
Developer Memory

Memory Store Test
"""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from brain.developer.memory.memory_store import (
    MemoryStore,
)

from brain.developer.memory.memory_loader import (
    MemoryLoader,
)


def main():

    print("=" * 80)
    print("JARVIS PRO")
    print("Memory Store Test")
    print("=" * 80)

    with TemporaryDirectory() as temp:

        project_path = Path(temp)

        # ------------------------------------------
        # Store
        # ------------------------------------------

        store = MemoryStore(
            str(project_path),
        )

        print("\n[1] Store created")

        # ------------------------------------------
        # Initial state
        # ------------------------------------------

        data = store.load()

        print("[2] Initial memory:", data)

        # ------------------------------------------
        # Save
        # ------------------------------------------

        test_data = {

            "version": 1,

            "project": {

                "name": "TestProject",

            },

            "files": {

                "main.py": {

                    "language": "python",

                },

            },

        }

        success = store.save(
            test_data,
        )

        print("[3] Save success:", success)

        # ------------------------------------------
        # Verify file
        # ------------------------------------------

        print(
            "[4] Memory exists:",
            store.exists(),
        )

        # ------------------------------------------
        # Load again
        # ------------------------------------------

        loaded = store.load()

        print("[5] Loaded memory:")
        print(loaded)

        # ------------------------------------------
        # Loader
        # ------------------------------------------

        loader = MemoryLoader(
            store,
        )

        loaded_by_loader = loader.load()

        print("[6] Loader result:")
        print(loaded_by_loader)

        # ------------------------------------------
        # Verify
        # ------------------------------------------

        assert success is True

        assert store.exists() is True

        assert loaded["project"]["name"] == "TestProject"

        assert (
            loaded_by_loader["project"]["name"]
            == "TestProject"
        )

        # ------------------------------------------
        # Clear
        # ------------------------------------------

        cleared = store.clear()

        print("[7] Clear success:", cleared)

        print(
            "[8] Memory exists after clear:",
            store.exists(),
        )

        assert cleared is True

        assert store.exists() is False

    print()
    print("=" * 80)
    print("MEMORY STORE TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":

    main()