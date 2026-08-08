"""
JARVIS PRO
Developer Integration

Phase 10.7
Full End-to-End Integration Test
"""

from pathlib import Path
from tempfile import TemporaryDirectory


def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("FULL DEVELOPER END-TO-END INTEGRATION TEST")
    print("=" * 90)

    # ==================================================
    # Imports
    # ==================================================

    import core.dispatcher as dispatcher

    import voice.manager as voice_manager

    # ==================================================
    # Disable unrelated AI memory learning
    # ==================================================

    original_learn = dispatcher.learn

    dispatcher.learn = lambda command: {}

    # ==================================================
    # Disable voice output during test
    # ==================================================

    original_speak = voice_manager.speak

    voice_manager.speak = lambda text: print(
        f"[TEST VOICE] {text}"
    )

    try:

        with TemporaryDirectory() as temp:

            project_path = Path(temp)

            # ==========================================
            # 1. Create temporary project
            # ==========================================

            source = project_path / "main.py"

            original_code = (
                "def addition(a, b):\n"
                "    return a + b\n"
            )

            source.write_text(
                original_code,
                encoding="utf-8",
            )

            print("\n[1] Temporary project created")
            print(project_path)
            print("PASS")

            # ==========================================
            # 2. Get actual Dispatcher BrainRouter
            # ==========================================

            router = dispatcher.brain_router

            assert router is not None

            print("\n[2] Dispatcher BrainRouter")
            print(type(router).__name__)
            print("PASS")

            # ==========================================
            # 3. Configure active project
            # ==========================================

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

            # ==========================================
            # 4. Verify active project
            # ==========================================

            resolved = (
                router.project_resolver.resolve()
            )

            assert resolved is not None

            assert (
                Path(resolved).resolve()
                == project_path.resolve()
            )

            print("\n[4] Active project resolved")
            print(resolved)
            print("PASS")

            # ==========================================
            # 5. Install controlled Developer provider
            # ==========================================

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

            print("\n[5] Controlled Developer provider")
            print("PASS")

            # ==========================================
            # 6. Execute through REAL dispatcher
            # ==========================================

            command = "add subtract function"

            print("\n[6] Dispatching command")
            print(command)

            dispatcher.dispatch(
                command
            )

            print("PASS")

            # ==========================================
            # 7. Verify file modification
            # ==========================================

            updated = source.read_text(
                encoding="utf-8",
            )

            print("\n[7] Updated main.py")
            print("-" * 60)
            print(updated)
            print("-" * 60)

            assert (
                "def addition(a, b):"
                in updated
            )

            assert (
                "def subtract(a, b):"
                in updated
            )

            assert (
                "return a + b"
                in updated
            )

            print("PASS")

            # ==========================================
            # 8. Verify Developer result memory
            # ==========================================

            developer_memory = (
                router.developer.memory.memory
            )

            print("\n[8] Developer Memory")
            print(developer_memory)

            assert (
                len(
                    developer_memory["edits"]
                )
                == 1
            )

            edit = (
                developer_memory["edits"][0]
            )

            assert (
                edit["request"]
                == command
            )

            assert (
                edit["edit_type"]
                == "ADD"
            )

            assert (
                "main.py"
                in edit["files"]
            )

            assert (
                edit["success"]
                is True
            )

            print("PASS")

            # ==========================================
            # 9. Verify active project memory
            # ==========================================

            session = (
                developer_memory["session"]
            )

            assert (
                session["project_path"]
                == str(project_path)
            )

            print(
                "\n[9] Active project memory"
            )

            print(session)

            print("PASS")

            # ==========================================
            # 10. Verify persistent memory
            # ==========================================

            reloaded_memory = (
                type(
                    router.developer.memory
                )(
                    str(project_path)
                )
            )

            reloaded_memory.load()

            print(
                "\n[10] Reloaded Developer Memory"
            )

            print(
                reloaded_memory.memory
            )

            assert (
                len(
                    reloaded_memory.memory["edits"]
                )
                == 1
            )

            assert (
                reloaded_memory.memory["edits"][0][
                    "success"
                ]
                is True
            )

            print("PASS")

            # ==========================================
            # 11. Verify backup
            # ==========================================

            backup_root = (
                project_path
                / ".jarvis_backups"
            )

            assert backup_root.exists()

            backups = list(
                backup_root.iterdir()
            )

            assert backups

            print("\n[11] Backup created")
            print(backups)
            print("PASS")

            # ==========================================
            # 12. Verify no unrelated files changed
            # ==========================================

            project_files = [

                path.relative_to(
                    project_path
                ).as_posix()

                for path in project_path.rglob("*")

                if path.is_file()

                and ".jarvis_backups"
                not in path.parts

            ]

            print(
                "\n[12] Project files"
            )

            print(project_files)

            assert (
                "main.py"
                in project_files
            )

            print("PASS")

    finally:

        # ==============================================
        # Restore global functions
        # ==============================================

        dispatcher.learn = original_learn

        voice_manager.speak = original_speak

    print()
    print("=" * 90)
    print(
        "PHASE 10.7 FULL END-TO-END "
        "INTEGRATION TEST PASSED"
    )
    print("=" * 90)


if __name__ == "__main__":
    main()