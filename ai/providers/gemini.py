"""
JARVIS PRO
AI Core - Gemini Provider

Google Gemini implementation of the JARVIS AIProvider.

Supports:
- Full generation
- Streaming generation
- System instructions
- Model override
- Stop-event interruption
"""

import os
from typing import Iterator, Optional

from google import genai
from google.genai import types

from ai.core.schemas import (
    AIRequest,
    AIResponse,
    AIStreamChunk,
)

from ai.providers.base import AIProvider


class GeminiProvider(AIProvider):
    """
    Google Gemini implementation of AIProvider.
    """

    DEFAULT_MODEL = "gemini-3.6-flash"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
    ):

        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
        )

        self.model = model

        self._client = None

    # ======================================================
    # Provider Information
    # ======================================================

    @property
    def name(self) -> str:

        return "gemini"

    # ======================================================
    # Client
    # ======================================================

    def _get_client(self):

        if self._client is not None:

            return self._client

        if not self.api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self._client = genai.Client(
            api_key=self.api_key
        )

        return self._client

    # ======================================================
    # Availability
    # ======================================================

    def is_available(self) -> bool:

        return bool(self.api_key)

    # ======================================================
    # Full Generation
    # ======================================================

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        model = (
            request.model
            or self.model
        )

        try:

            client = self._get_client()

            config = None

            if request.system_prompt:

                config = types.GenerateContentConfig(
                    system_instruction=(
                        request.system_prompt
                    )
                )

            response = client.models.generate_content(

                model=model,

                contents=request.prompt,

                config=config,
            )

            text = response.text or ""

            return AIResponse(

                text=text,

                provider=self.name,

                model=model,

                success=True,

                metadata={
                    "response": response,
                },
            )

        except Exception as e:

            print(
                f"[GEMINI ERROR] {e}"
            )

            return AIResponse(

                text="",

                provider=self.name,

                model=model,

                success=False,

                error=str(e),

                metadata={
                    "error_type": (
                        type(e).__name__
                    )
                },
            )

    # ======================================================
    # Streaming
    # ======================================================

    def stream(
        self,
        request: AIRequest,
    ) -> Iterator[AIStreamChunk]:

        model = (
            request.model
            or self.model
        )

        try:

            client = self._get_client()

            config = None

            if request.system_prompt:

                config = types.GenerateContentConfig(
                    system_instruction=(
                        request.system_prompt
                    )
                )

            response_stream = (
                client.models.generate_content_stream(

                    model=model,

                    contents=request.prompt,

                    config=config,
                )
            )

            for chunk in response_stream:

                # ------------------------------------------
                # Stop requested
                # ------------------------------------------

                if (
                    request.stop_event is not None
                    and request.stop_event.is_set()
                ):

                    print(
                        "\n[GEMINI STREAM] Interrupted"
                    )

                    break

                text = getattr(
                    chunk,
                    "text",
                    ""
                ) or ""

                if text:

                    yield AIStreamChunk(

                        text=text,

                        provider=self.name,

                        model=model,

                        done=False,

                        metadata={
                            "response": chunk,
                        },
                    )

        except Exception as e:

            print(
                f"[GEMINI STREAM ERROR] {e}"
            )

            yield AIStreamChunk(

                text="",

                provider=self.name,

                model=model,

                done=True,

                metadata={
                    "error": str(e),

                    "success": False,

                    "error_type": (
                        type(e).__name__
                    ),
                },
            )

            return

        # --------------------------------------------------
        # Normal completion
        # --------------------------------------------------

        yield AIStreamChunk(

            text="",

            provider=self.name,

            model=model,

            done=True,

            metadata={
                "success": True,
            },
        )