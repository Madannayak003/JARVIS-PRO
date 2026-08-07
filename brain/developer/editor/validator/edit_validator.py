"""
JARVIS PRO
Developer Editor

Edit Validator
"""

from brain.developer.editor.models.edit_result import (
    EditResult,
)

from brain.developer.editor.validator.syntax_validator import (
    SyntaxValidator,
)


class EditValidator:
    """
    Validates parsed patches before
    they are written to disk.
    """

    def __init__(self):

        self.syntax_validator = SyntaxValidator()

    # --------------------------------------------------

    def validate(
        self,
        result: EditResult,
    ) -> EditResult:

        seen = set()

        valid = []

        for patch in result.patches:

            # -----------------------------
            # Path required
            # -----------------------------

            if not patch.path:

                result.errors.append(

                    "Patch has no file path."

                )

                continue

            # -----------------------------
            # Duplicate file
            # -----------------------------

            if patch.path in seen:

                result.errors.append(

                    f"Duplicate patch: {patch.path}"

                )

                continue

            seen.add(

                patch.path

            )

            # -----------------------------
            # Content required
            # -----------------------------

            if not patch.content.strip():

                result.errors.append(

                    f"{patch.path} is empty."

                )

                continue

            # -----------------------------
            # Syntax Validation
            # -----------------------------

            success, message = self.syntax_validator.validate(

                patch,

            )

            if not success:

                result.errors.append(

                    f"{patch.path}: {message}"

                )

                continue

            valid.append(

                patch

            )

        result.patches = valid

        result.success = (

            len(result.errors) == 0

        )

        return result