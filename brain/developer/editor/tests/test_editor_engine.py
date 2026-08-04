"""
JARVIS PRO
Developer Editor

Final Integration Test
"""

from brain.developer.editor.editor import Editor


def run_test(
    editor: Editor,
    request: str,
    project: str,
):

    print("=" * 100)
    print("REQUEST")
    print("=" * 100)
    print(request)
    print()

    try:

        result = editor.execute(

            request,

            project,

        )

    except Exception as error:

        print("EXECUTION FAILED")
        print(error)
        print()

        return

    print("SUCCESS :", result.success)

    print()

    if result.message:

        print("MESSAGE")
        print("-" * 80)
        print(result.message)
        print()

    print("PATCHES")
    print("-" * 80)

    if result.patches:

        for patch in result.patches:

            print(patch.path)

    else:

        print("(None)")

    print()

    if result.warnings:

        print("WARNINGS")
        print("-" * 80)

        for warning in result.warnings:

            print(warning)

        print()

    if result.errors:

        print("ERRORS")
        print("-" * 80)

        for error in result.errors:

            print(error)

        print()

    print("=" * 100)
    print()


def main():

    project = "workspace/Python/PythonCalculator"

    editor = Editor()

    tests = [

        "Fix divide()",

        "Rename add() to addition()",

        "Optimize calculator",

        "Format main.py",

    ]

    print()
    print("#" * 100)
    print("JARVIS PRO")
    print("Developer Editor Final Integration Test")
    print("#" * 100)
    print()

    for request in tests:

        run_test(

            editor,

            request,

            project,

        )

    print("#" * 100)
    print("ALL TESTS FINISHED")
    print("#" * 100)


if __name__ == "__main__":

    main()