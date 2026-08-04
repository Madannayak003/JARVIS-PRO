"""
JARVIS PRO
Developer

Ollama Provider
"""

from typing import Any

from ai.ollama import ask_ollama

from brain.developer.generator.providers.base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    """
    Shared Ollama provider.

    Can be used by both Generator and Editor because
    both PromptResult objects expose:

        prompt.system_prompt
        prompt.user_prompt
    """

    def __init__(

        self,

        system_prompt: str = "",

    ):

        self.system_prompt = system_prompt

    # --------------------------------------------------

    def generate(

        self,

        prompt: Any,

    ) -> str:

        system = (

            prompt.system_prompt

            if getattr(prompt, "system_prompt", "")

            else self.system_prompt

        )

        user = getattr(

            prompt,

            "user_prompt",

            "",

        )

        print("OllamaProvider : Sending request...")

        print("=" * 80)
        print("SYSTEM")
        print("=" * 80)
        print(system)

        print("=" * 80)
        print("USER")
        print("=" * 80)
        print(user)
        print("=" * 80)

        response = ask_ollama(

            system,

            user,

        )

        print("OllamaProvider : Response received")

        return response