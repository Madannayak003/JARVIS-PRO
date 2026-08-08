"""
JARVIS PRO
AI Core - AI Service

Main public interface for the JARVIS AI Model System.

Consumers such as:
- Chat
- Planner
- Memory
- Developer
- Editor
- Repair

should use AIService instead of calling providers directly.
"""

from typing import Iterator, Optional

from ai.core.router import AIRouter
from ai.core.schemas import (
    AIRequest,
    AIResponse,
    AIStreamChunk,
)

from ai.providers.ollama import OllamaProvider

from ai.providers.gemini import GeminiProvider

from ai.providers.openai import OpenAIProvider


class AIService:
    """
    Main entry point for the JARVIS AI system.
    """

    def __init__(
        self,
        router: Optional[AIRouter] = None,
    ):

        # --------------------------------------------------
        # Router
        # --------------------------------------------------

        self.router = (
            router
            if router is not None
            else AIRouter()
        )

        # --------------------------------------------------
        # Register currently available providers
        # --------------------------------------------------

        self._register_default_providers()

    # ======================================================
    # Provider Registration
    # ======================================================

    def _register_default_providers(self):

        # --------------------------------------------------
        # Ollama
        # --------------------------------------------------

        if self.router.get_provider("ollama") is None:

            self.router.register_provider(
                OllamaProvider()
            )

        # --------------------------------------------------
        # Gemini
        # --------------------------------------------------

        if self.router.get_provider("gemini") is None:

            self.router.register_provider(
                GeminiProvider()
            )

        # --------------------------------------------------
        # OpenAI
        # --------------------------------------------------

        if self.router.get_provider("openai") is None:

            self.router.register_provider(
                OpenAIProvider()
            )

    # ======================================================
    # Generate
    # ======================================================

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        capability: str = "conversation",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        output_format: str = "text",
        metadata: Optional[dict] = None,
    ) -> AIResponse:
        """
        Generate a complete AI response.
        """

        request = AIRequest(

            prompt=prompt,

            system_prompt=system_prompt,

            capability=capability,

            provider=provider,

            model=model,

            stream=False,

            output_format=output_format,

            metadata=(
                metadata
                if metadata is not None
                else {}
            ),
        )

        return self.router.generate(
            request
        )

    # ======================================================
    # Stream
    # ======================================================

    def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        capability: str = "conversation",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        stop_event=None,
        metadata: Optional[dict] = None,
    ) -> Iterator[AIStreamChunk]:
        """
        Stream an AI response.
        """

        request = AIRequest(

            prompt=prompt,

            system_prompt=system_prompt,

            capability=capability,

            provider=provider,

            model=model,

            stream=True,

            stop_event=stop_event,

            metadata=(
                metadata
                if metadata is not None
                else {}
            ),
        )

        return self.router.stream(
            request
        )


# ==========================================================
# Shared AI Service
# ==========================================================

ai_service = AIService()