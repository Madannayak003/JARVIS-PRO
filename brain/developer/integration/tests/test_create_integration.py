"""
JARVIS PRO
Developer Integration

CREATE Pipeline Integration Test

Phase 10
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from brain.developer.developer import Developer


# ==========================================================
# Controlled Generator Provider
# ==========================================================

class ControlledProvider:
    """
    Controlled AI provider.

    Returns a complete project using the same
    # FILE: format used by the Developer parser.
    """

    def generate(self, prompt):

        print(
            "\n[TEST PROVIDER] "
            "Generator request received."
        )

        return (
            "# FILE: main.py\n"
            "```python\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "\n"
            "\n"
            "def subtract(a, b):\n"
            "    return a - b\n"
            "\n"
            "\n"
            "def multiply(a, b):\n"
            "    return a * b\n"
            "\n"
            "\n"
            "def divide(a, b):\n"
            "    if b == 0:\n"
            "        return \"Error: division by zero\"\n"
            "\n"
            "    return a / b\n"
            "\n"
            "\n"
            "def main():\n"
            "\n"
            "    print(\"Python Calculator\")\n"
            "    print(\"1. Add\")\n"
            "    print(\"2. Subtract\")\n"
            "    print(\"3. Multiply\")\n"
            "    print(\"4. Divide\")\n"
            "\n"
            "    choice = input(\"Enter choice: \")\n"
            "    a = float(input(\"Enter first number: \"))\n"
            "    b = float(input(\"Enter second number: \"))\n"
            "\n"
            "    if choice == \"1\":\n"
            "        print(add(a, b))\n"
            "\n"
            "    elif choice == \"2\":\n"
            "        print(subtract(a, b))\n"
            "\n"
            "    elif choice == \"3\":\n"
            "        print(multiply(a, b))\n"
            "\n"
            "    elif choice == \"4\":\n"
            "        print(divide(a, b))\n"
            "\n"
            "    else:\n"
            "        print(\"Invalid choice\")\n"
            "\n"
            "\n"
            "if __name__ == \"__main__\":\n"
            "    main()\n"
            "```\n"
            "\n"

            "# FILE: test_main.py\n"
            "```python\n"
            "from main import add, subtract, multiply, divide\n"
            "\n"
            "\n"
            "def test_add():\n"
            "    assert add(2, 3) == 5\n"
            "\n"
            "\n"
            "def test_subtract():\n"
            "    assert subtract(5, 3) == 2\n"
            "\n"
            "\n"
            "def test_multiply():\n"
            "    assert multiply(2, 3) == 6\n"
            "\n"
            "\n"
            "def test_divide():\n"
            "    assert divide(6, 3) == 2\n"
            "```\n"
            "\n"

            "# FILE: requirements.txt\n"
            "pytest\n"
            "\n"

            "# FILE: tests/test_calculator.py\n"
            "```python\n"
            "from main import add, subtract, multiply, divide\n"
            "\n"
            "\n"
            "def test_add():\n"
            "    assert add(2, 3) == 5\n"
            "\n"
            "\n"
            "def test_subtract():\n"
            "    assert subtract(5, 3) == 2\n"
            "\n"
            "\n"
            "def test_multiply():\n"
            "    assert multiply(2, 3) == 6\n"
            "\n"
            "\n"
            "def test_divide():\n"
            "    assert divide(6, 3) == 2\n"
            "```\n"
            "\n"

            "# FILE: src/main.py\n"
            "```python\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "\n"
            "\n"
            "def subtract(a, b):\n"
            "    return a - b\n"
            "\n"
            "\n"
            "def multiply(a, b):\n"
            "    return a * b\n"
            "\n"
            "\n"
            "def divide(a, b):\n"
            "    if b == 0:\n"
            "        return \"Error: division by zero\"\n"
            "\n"
            "    return a / b\n"
            "```\n"
            "\n"

            "# FILE: src/package_init.py\n"
            "```python\n"
            "```\n"
            "\n"

            "# FILE: docs/README.md\n"
            "```markdown\n"
            "# Python Calculator\n"
            "\n"
            "A simple Python calculator.\n"
            "\n"
            "Supports addition, subtraction, multiplication and division.\n"
            "```\n"
        )


# ==========================================================
# Test
# ==========================================================

def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("Developer CREATE Integration Test")
    print("=" * 90)

    with TemporaryDirectory() as temp_dir:

        root = Path(temp_dir)

        # ==================================================
        # Temporary Workspace
        # ==================================================

        print("\n[1] Temporary workspace")
        print(root)

        assert root.exists()

        print("PASS")

        # ==================================================
        # Developer
        # ==================================================

        developer = Developer()

        print("\n[2] Developer created")
        print("PASS")

        # ==================================================
        # Controlled Generator
        # ==================================================

        developer.pipeline.generator.provider = (
            ControlledProvider()
        )

        print("\n[3] Controlled Generator installed")
        print("PASS")

        # ==================================================
        # Redirect Workspace
        # ==================================================

        def controlled_resolve(workspace):

            print(
                "[TEST WORKSPACE] "
                "Output redirected to temporary project."
            )

            return str(root)

        developer.pipeline.workspace.workspace_resolver.resolve = (
            controlled_resolve
        )

        print("\n[4] Workspace redirected")
        print("PASS")

        # ==================================================
        # CREATE
        # ==================================================

        request = "create python calculator"

        print("\n[5] Developer CREATE request")
        print(request)

        result = developer.execute(
            request,
            "",
        )

        print("\n[6] Developer result")
        print(result)

        assert result is not None, (
            "Developer returned None."
        )

        assert result.success is True, (
            "Developer CREATE failed."
        )

        project_root = Path(result.project_path)

        assert project_root.exists(), (
            f"Project directory was not created: {project_root}"
        )

        print("Project path:", project_root)
        print("PASS")

        # ==================================================
        # Generated Files
        # ==================================================

        print("\n[7] Generated files")

        files = sorted(
            path
            for path in project_root.rglob("*")
            if path.is_file()
        )

        for file in files:

            print(
                file.relative_to(project_root)
            )

        assert files, (
            "No files were created."
        )

        print("PASS")

        # ==================================================
        # Required Files
        # ==================================================

        required_files = [
            "main.py",
            "test_main.py",
            "requirements.txt",
            "tests/test_calculator.py",
            "src/main.py",
            "src/package_init.py",
            "docs/README.md",
        ]

        print("\n[8] Required project files")

        for relative_path in required_files:

            path = project_root / relative_path

            print(
                relative_path,
                "->",
                path.exists(),
            )

            assert path.exists(), (
                f"Missing generated file: "
                f"{relative_path}"
            )

        print("PASS")

        # ==================================================
        # Main File
        # ==================================================

        print("\n[9] main.py")

        main_file = project_root / "main.py"

        content = main_file.read_text(
            encoding="utf-8",
        )

        print(content)

        assert "def add" in content
        assert "def subtract" in content
        assert "def multiply" in content
        assert "def divide" in content

        print("PASS")

        # ==================================================
        # Test File
        # ==================================================

        print("\n[10] test_main.py")

        test_file = project_root / "test_main.py"

        test_content = test_file.read_text(
            encoding="utf-8",
        )

        print(test_content)

        assert "test_add" in test_content
        assert "test_subtract" in test_content

        print("PASS")

        # ==================================================
        # No Active Project
        # ==================================================

        print("\n[11] Active project requirement")

        print(
            "CREATE executed with project_path=''."
        )

        print(
            "No active project was required."
        )

        print("PASS")

        # ==================================================
        # Final
        # ==================================================

        print()
        print("=" * 90)
        print(
            "PHASE 10 CREATE INTEGRATION TEST PASSED"
        )
        print("=" * 90)


if __name__ == "__main__":
    main()