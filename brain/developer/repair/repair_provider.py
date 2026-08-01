"""
JARVIS PRO
Developer Repair

Repair Provider
"""

from ai.ollama import ask_ollama

from brain.developer.prompt_builder.models.prompt_result import (
    PromptResult,
)


class RepairProvider:
    """
    Sends repair prompts to the AI.
    """

    def generate(
        self,
        prompt: PromptResult,
    ) -> str:

        return ask_ollama(

            prompt.system_prompt,

            prompt.user_prompt,

        )