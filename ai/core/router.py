"""
JARVIS PRO
AI Core - AI Router

Central runtime AI routing system.

Responsibilities:
- Select providers using ModelManager policy
- Check provider availability
- Try preferred models in order
- Fallback when a provider is unavailable
- Fallback when generation fails
- Support streaming
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
    Central AI runtime router.
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

        if not provider_name:
            return None

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
        # Policy-aware candidates
        # --------------------------------------------------

        candidates = self.model_manager.candidates(
            request.capability
        )

        # --------------------------------------------------
        # Explicit provider filter
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
    # Route Only
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
                    model.name,
                )

                continue

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
    # Generate With Fallback
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

                provider="",

                model="",

                success=False,

                error=(
                    "No AI models available for "
                    f"capability: {request.capability}"
                ),
            )

        last_error = None

        # --------------------------------------------------
        # Try every candidate in policy order
        # --------------------------------------------------

        for model in candidates:

            provider = self.get_provider(
                model.provider
            )

            # ----------------------------------------------
            # Provider not registered
            # ----------------------------------------------

            if provider is None:

                print(
                    "[AI ROUTER] Provider not registered:",
                    model.provider,
                )

                continue

            # ----------------------------------------------
            # Provider unavailable
            # ----------------------------------------------

            if not provider.is_available():

                print(
                    "[AI ROUTER] Skipping unavailable:",
                    model.provider,
                    model.name,
                )

                continue

            # ----------------------------------------------
            # Select model
            # ----------------------------------------------

            request.model = model.name

            request.provider = model.provider

            print(
                "[AI ROUTER] Trying:",
                model.provider,
                model.name,
            )

            # ----------------------------------------------
            # Generate
            # ----------------------------------------------

            try:

                response = provider.generate(
                    request
                )

            except Exception as e:

                last_error = str(e)

                print(
                    "[AI ROUTER] Provider exception:",
                    model.provider,
                    e,
                )

                continue

            # ----------------------------------------------
            # Success
            # ----------------------------------------------

            if response.success:

                print(
                    "[AI ROUTER] Success:",
                    model.provider,
                    model.name,
                )

                return response

            # ----------------------------------------------
            # Provider returned failure
            # ----------------------------------------------

            last_error = response.error

            print(
                "[AI ROUTER] Generation failed:",
                model.provider,
                model.name,
            )

            print(
                "[AI ROUTER] Error:",
                response.error,
            )

            # ----------------------------------------------
            # Continue to next provider
            # ----------------------------------------------

            continue

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
    # Streaming
    # ======================================================

    def stream(
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

                continue

            if not provider.is_available():

                print(
                    "[AI ROUTER] Streaming skip:",
                    model.provider,
                    model.name,
                )

                continue

            request.model = model.name

            request.provider = model.provider

            print(
                "[AI ROUTER] Streaming:",
                model.provider,
                model.name,
            )

            return provider.stream(
                request
            )

        raise RuntimeError(
            "No available AI provider for streaming."
        )