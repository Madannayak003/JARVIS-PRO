"""
JARVIS PRO
Developer Editor

Validator Test
"""

from brain.developer.editor.models.patch import (
    Patch,
)

from brain.developer.editor.models.edit_result import (
    EditResult,
)

from brain.developer.editor.validator.edit_validator import (
    EditValidator,
)


def main():

    result = EditResult()

    result.patches = [

        Patch(

            path="src/main.py",

            language="python",

            content='print("Hello")',

        ),

        Patch(

            path="src/main.py",

            language="python",

            content='print("Duplicate")',

        ),

        Patch(

            path="",

            language="python",

            content='print("Missing Path")',

        ),

        Patch(

            path="README.md",

            language="md",

            content="",

        ),

    ]

    validator = EditValidator()

    result = validator.validate(

        result,

    )

    print("=" * 80)

    print("VALIDATOR RESULT")

    print("=" * 80)

    print("Success :", result.success)

    print()

    print("VALID PATCHES")

    print("-" * 80)

    for patch in result.patches:

        print(patch.path)

    print()

    print("ERRORS")

    print("-" * 80)

    for error in result.errors:

        print(error)


if __name__ == "__main__":

    main()