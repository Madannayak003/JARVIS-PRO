"""
JARVIS PRO
Developer Generator

Ollama Provider
"""

from ai.ollama import ask_ollama

from brain.developer.generator.providers.base_provider import BaseProvider
from brain.developer.prompt_builder.models.prompt_result import PromptResult


class OllamaProvider(BaseProvider):
    """
    Ollama implementation of the BaseProvider.
    """

    def __init__(self, system_prompt: str = ""):

        self.system_prompt = system_prompt

    def generate(
        self,
        prompt: PromptResult,
    ) -> str:
        """
        Generate raw text from Ollama.
        """

        system = (

            prompt.system_prompt

            if prompt.system_prompt

            else self.system_prompt

        )

        print("OllamaProvider : Sending request...")
        
        print("=" * 80)
        print("SYSTEM")
        print("=" * 80)
        print(system)

        print("=" * 80)
        print("USER")
        print("=" * 80)
        print(prompt.user_prompt)
        print("=" * 80)

        response = ask_ollama(

            system,

            prompt.user_prompt,

        )

        print("OllamaProvider : Response received")

        return response
        