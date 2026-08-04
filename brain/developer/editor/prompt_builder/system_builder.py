"""
JARVIS PRO
Developer Editor

System Builder
"""

from brain.developer.editor.models.prompt_context import (
    PromptContext,
)


class SystemBuilder:

    def build(
        self,
        context: PromptContext,
    ) -> str:

        return "\n".join(

            [

                "You are JARVIS PRO Developer Editor.",

                "You are an expert software engineer.",

                "Modify ONLY the requested files.",

                "Preserve existing coding style.",

                "Do not rewrite unrelated code.",

                "Return ONLY modified files.",

                "Do not explain anything.",

            ]

        )