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

                "Your task is to APPLY the user's requested edit.",

                "You MUST modify the code whenever the request requires a change.",

                "Do NOT simply repeat the original file.",

                "Preserve existing coding style.",

                "Modify ONLY the selected files.",

                "Keep unrelated code unchanged.",

                "If tests reference modified code, update those tests.",

                "Return ONLY modified '# FILE:' blocks.",

                "Never explain your work.",

            ]

        )