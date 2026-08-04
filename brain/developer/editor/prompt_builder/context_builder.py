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

            "# Selected Files",

            "",

        ]

        if request.target_files:

            for file in request.target_files:

                lines.append(

                    f"## {file}"

                )

                lines.append("")

                extension = file.split(".")[-1]

                lines.append(

                    f"```{extension}"

                )

                lines.append(

                    request.file_contents.get(

                        file,

                        "",

                    )

                )

                lines.append("```")

                lines.append("")

        else:

            lines.append(

                "(None)"

            )

        return "\n".join(lines)