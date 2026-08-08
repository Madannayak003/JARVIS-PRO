"""
JARVIS PRO
AI Core - AI Router

Central routing and fallback system.

Responsibilities:
- Select models
- Select providers
- Check provider availability
- Try fallback models
- Generate responses
- Stream responses
"""

from typing import Dict, Optional

from ai.core.model_manager import ModelManager
from ai.core.schemas import (
    AIRequest,
    AIResponse,
)

from ai.providers.base import AIProvider


class AIRouter:
    """
    Central AI routing system.
    """

    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
    ):

        self.model_manager = (
            model_manager
            if model_manager is not None
            else ModelManager()
        )

        self.providers: Dict[
            str,
            AIProvider
        ] = {}

    # ======================================================
    # Provider Registration
    # ======================================================

    def register_provider(
        self,
        provider: AIProvider,
    ) -> None:

        self.providers[
            provider.name.lower()
        ] = provider

    # ======================================================
    # Provider Lookup
    # ======================================================

    def get_provider(
        self,
        provider_name: str,
    ) -> Optional[AIProvider]:

        return self.providers.get(
            provider_name.lower()
        )

    # ======================================================
    # Candidate Models
    # ======================================================

    def _get_candidates(
        self,
        request: AIRequest,
    ):

        # --------------------------------------------------
        # Explicit model
        # --------------------------------------------------

        if request.model:

            model = self.model_manager.get_model(
                request.model
            )

            if model is None:
                return []

            if not model.enabled:
                return []

            return [model]

        # --------------------------------------------------
        # Capability models
        # --------------------------------------------------

        candidates = self.model_manager.find_models(
            request.capability
        )

        # --------------------------------------------------
        # Provider override
        # --------------------------------------------------

        if request.provider:

            provider_name = (
                request.provider.lower()
            )

            candidates = [
                model
                for model in candidates
                if model.provider.lower()
                == provider_name
            ]

        return candidates

    # ======================================================
    # Route
    # ======================================================

    def route(
        self,
        request: AIRequest,
    ):

        candidates = self._get_candidates(
            request
        )

        if not candidates:

            raise RuntimeError(
                "No AI models available for "
                f"capability: {request.capability}"
            )

        # --------------------------------------------------
        # Find first available provider
        # --------------------------------------------------

        for model in candidates:

            provider = self.get_provider(
                model.provider
            )

            if provider is None:

                print(
                    "[AI ROUTER] Provider not registered:",
                    model.provider,
                )

                continue

            if not provider.is_available():

                print(
                    "[AI ROUTER] Provider unavailable:",
                    model.provider,
                    "model:",
                    model.name,
                )

                continue

            # ----------------------------------------------
            # Select this model
            # ----------------------------------------------

            request.model = model.name

            request.provider = model.provider

            print(
                "[AI ROUTER] Selected:",
                model.provider,
                model.name,
            )

            return provider

        raise RuntimeError(
            "No available AI provider for "
            f"capability: {request.capability}"
        )

    # ======================================================
    # Generate
    # ======================================================

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        candidates = self._get_candidates(
            request
        )

        if not candidates:

            return AIResponse(
                text="",
                success=False,
                error=(
                    "No AI model available for "
                    f"capability: {request.capability}"
                ),
            )

        # --------------------------------------------------
        # Try models in priority order
        # --------------------------------------------------

        last_error = None

        for model in candidates:

            provider = self.get_provider(
                model.provider
            )

            if provider is None:

                continue

            if not provider.is_available():

                print(
                    "[AI ROUTER] Skipping unavailable:",
                    model.provider,
                    model.name,
                )

                continue

            request.model = model.name

            request.provider = model.provider

            print(
                "[AI ROUTER] Trying:",
                model.provider,
                model.name,
            )

            response = provider.generate(
                request
            )

            if response.success:

                return response

            last_error = response.error

            print(
                "[AI ROUTER] Model failed:",
                model.name,
                last_error,
            )

        # --------------------------------------------------
        # Everything failed
        # --------------------------------------------------

        return AIResponse(

            text="",

            provider="",

            model="",

            success=False,

            error=(
                last_error
                or
                "All AI providers failed."
            ),
        )

    # ======================================================
    # Stream
    # ======================================================

    def stream(
        self,
        request: AIRequest,
    ):

        provider = self.route(
            request
        )

        return provider.stream(
            request
        )