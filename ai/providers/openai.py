"""
JARVIS PRO
AI Core - OpenAI Provider

OpenAI / GPT implementation of the JARVIS AIProvider.

Supports:
- Full generation
- Streaming generation
- System prompts
- Model override
- Stop-event interruption
"""

import os
from typing import Iterator, Optional

from openai import OpenAI

from ai.core.schemas import (
    AIRequest,
    AIResponse,
    AIStreamChunk,
)

from ai.providers.base import AIProvider


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of AIProvider.
    """

    DEFAULT_MODEL = "gpt-5.4-mini"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
    ):

        self.api_key = (
            api_key
            or os.getenv("OPENAI_API_KEY")
        )

        self.model = model

        self._client = None

    # ======================================================
    # Provider Information
    # ======================================================

    @property
    def name(self) -> str:

        return "openai"

    # ======================================================
    # Client
    # ======================================================

    def _get_client(self):

        if self._client is not None:

            return self._client

        if not self.api_key:

            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self._client = OpenAI(
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

            messages = []

            # --------------------------------------------------
            # System message
            # --------------------------------------------------

            if request.system_prompt:

                messages.append({

                    "role": "system",

                    "content": (
                        request.system_prompt
                    ),

                })

            # --------------------------------------------------
            # User message
            # --------------------------------------------------

            messages.append({

                "role": "user",

                "content": request.prompt,

            })

            response = client.chat.completions.create(

                model=model,

                messages=messages,

            )

            text = (
                response.choices[0]
                .message
                .content
                or ""
            )

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
                f"[OPENAI ERROR] {e}"
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

            messages = []

            # --------------------------------------------------
            # System message
            # --------------------------------------------------

            if request.system_prompt:

                messages.append({

                    "role": "system",

                    "content": (
                        request.system_prompt
                    ),

                })

            # --------------------------------------------------
            # User message
            # --------------------------------------------------

            messages.append({

                "role": "user",

                "content": request.prompt,

            })

            response_stream = (
                client.chat.completions.create(

                    model=model,

                    messages=messages,

                    stream=True,

                )
            )

            for chunk in response_stream:

                # ----------------------------------------------
                # Stop requested
                # ----------------------------------------------

                if (
                    request.stop_event is not None
                    and request.stop_event.is_set()
                ):

                    print(
                        "\n[OPENAI STREAM] Interrupted"
                    )

                    break

                if not chunk.choices:

                    continue

                delta = (
                    chunk.choices[0]
                    .delta
                    .content
                    or ""
                )

                if delta:

                    yield AIStreamChunk(

                        text=delta,

                        provider=self.name,

                        model=model,

                        done=False,

                        metadata={
                            "response": chunk,
                        },
                    )

        except Exception as e:

            print(
                f"[OPENAI STREAM ERROR] {e}"
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