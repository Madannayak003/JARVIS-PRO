"""
JARVIS PRO
Developer Editor

Context Builder
"""

from brain.developer.editor.models.prompt_context import (
    PromptContext,
)


class ContextBuilder:
    """
    Builds the edit context for the LLM.
    """

    MAX_PREVIEW_LENGTH = 8000

    # --------------------------------------------------

    def build(
        self,
        context: PromptContext,
    ) -> str:

        request = context.request

        lines = [

            "# Edit Context",

            "",

            f"User Request : {request.user_request}",

            f"Action       : {request.edit_type}",

            "",

            "# Execution Plan",

            "",

        ]

        # ------------------------------------------
        # Execution Plan
        # ------------------------------------------

        if request.implementation_steps:

            for step in request.implementation_steps:

                lines.append(

                    f"- {step}"

                )

        else:

            lines.append(

                "- Apply the requested edit."

            )

        lines.extend(

            [

                "",

                "# Selected Files",

                "",

            ]

        )

        # ------------------------------------------
        # Selected Files
        # ------------------------------------------

        if not request.target_files:

            lines.append(

                "(None)"

            )

            return "\n".join(lines)

        for file in request.target_files:

            content = request.file_contents.get(

                file,

                "",

            )

            extension = file.rsplit(".", 1)[-1]

            lines.append(f"## {file}")

            lines.append("")

            if not content:

                lines.append(

                    "(File is empty or could not be read.)"

                )

                lines.append("")

                continue

            # ------------------------------------------
            # Limit prompt size
            # ------------------------------------------

            if len(content) > self.MAX_PREVIEW_LENGTH:

                content = (

                    content[: self.MAX_PREVIEW_LENGTH]

                    + "\n\n... (truncated) ..."

                )

            lines.append(f"```{extension}")

            lines.append(content)

            lines.append("```")

            lines.append("")

        return "\n".join(lines)