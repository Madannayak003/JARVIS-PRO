"""
JARVIS PRO
AI Core - Gemini Provider

Google Gemini implementation of the JARVIS AIProvider.

Supports:

- Full generation
- Streaming generation
- System instructions
- Model override
- Optional image inputs
- Stop-event interruption
"""

import os
from pathlib import Path
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

    Supports both normal text requests and
    multimodal requests containing images.
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
    # Build Contents
    # ======================================================

    def _build_contents(self, request: AIRequest):
        """
        Build Gemini contents.

        Existing text-only requests remain exactly
        as they were.

        When images are supplied, Gemini receives:

            image(s) + prompt
        """

        images = (
            request.images
            if request.images
            else []
        )

        # --------------------------------------------------
        # Existing text-only behavior
        # --------------------------------------------------

        if not images:

            return request.prompt

        # --------------------------------------------------
        # Multimodal request
        # --------------------------------------------------

        contents = []

        for image in images:

            contents.append(
                self._prepare_image(image)
            )

        contents.append(
            request.prompt
        )

        return contents

    # ======================================================
    # Prepare Image
    # ======================================================

    def _prepare_image(self, image):
        """
        Convert supported image inputs into a Gemini
        compatible content object.

        Supported:

        - PIL.Image.Image
        - Gemini Part
        - bytes
        - pathlib.Path
        - string file path
        """

        # --------------------------------------------------
        # Already a Gemini Part / supported SDK object
        # --------------------------------------------------

        if isinstance(
            image,
            types.Part,
        ):

            return image

        # --------------------------------------------------
        # PIL Image
        # --------------------------------------------------

        try:

            from PIL import Image

            if isinstance(
                image,
                Image.Image,
            ):

                return image

        except ImportError:

            pass

        # --------------------------------------------------
        # Raw bytes
        # --------------------------------------------------

        if isinstance(
            image,
            bytes,
        ):

            return types.Part.from_bytes(
                data=image,
                mime_type="image/png",
            )

        # --------------------------------------------------
        # File path
        # --------------------------------------------------

        if isinstance(
            image,
            (str, Path),
        ):

            path = Path(image)

            if not path.exists():

                raise FileNotFoundError(
                    f"Image file not found: {path}"
                )

            suffix = (
                path.suffix.lower()
            )

            mime_types = {

                ".jpg": "image/jpeg",

                ".jpeg": "image/jpeg",

                ".png": "image/png",

                ".webp": "image/webp",

                ".gif": "image/gif",

            }

            mime_type = mime_types.get(
                suffix,
                "image/png",
            )

            with open(
                path,
                "rb",
            ) as file:

                image_bytes = file.read()

            return types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            )

        # --------------------------------------------------
        # Unsupported input
        # --------------------------------------------------

        raise TypeError(
            "Unsupported Gemini image input: "
            f"{type(image).__name__}"
        )

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

                config = (
                    types.GenerateContentConfig(
                        system_instruction=(
                            request.system_prompt
                        )
                    )
                )

            contents = (
                self._build_contents(
                    request
                )
            )

            response = (
                client.models.generate_content(

                    model=model,

                    contents=contents,

                    config=config,
                )
            )

            text = (
                response.text
                or ""
            )

            return AIResponse(

                text=text,

                provider=self.name,

                model=model,

                success=True,

                metadata={
                    "response": response,
                    "multimodal": bool(
                        request.images
                    ),
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

                config = (
                    types.GenerateContentConfig(
                        system_instruction=(
                            request.system_prompt
                        )
                    )
                )

            contents = (
                self._build_contents(
                    request
                )
            )

            response_stream = (
                client.models.generate_content_stream(

                    model=model,

                    contents=contents,

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
                    "",
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