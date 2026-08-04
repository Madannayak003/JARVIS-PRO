"""
JARVIS PRO
Developer Editor

Context Builder
"""

from brain.developer.editor.models.prompt_context import (
    PromptContext,
)


class ContextBuilder:

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

                    f"- {file}"

                )

        else:

            lines.append(

                "(None)"

            )

        return "\n".join(lines)