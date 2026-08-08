"""
JARVIS PRO
AI Core - Model Manager

Responsible for selecting models using:
- Model Registry
- AI Model Policy
- Provider preferences
- Explicit model/provider overrides

The ModelManager does NOT call AI providers.
"""

from typing import List, Optional

from ai.core.policy import AIModelPolicy
from ai.core.registry import (
    ModelDefinition,
    ModelRegistry,
)


class ModelManager:
    """
    Selects the most appropriate model for a capability.
    """

    def __init__(
        self,
        registry: Optional[ModelRegistry] = None,
        policy=AIModelPolicy,
    ):

        self.registry = (
            registry
            if registry is not None
            else ModelRegistry()
        )

        self.policy = policy

    # ======================================================
    # Get Explicit Model
    # ======================================================

    def get_model(
        self,
        model_name: str,
    ) -> Optional[ModelDefinition]:

        return self.registry.get(
            model_name
        )

    # ======================================================
    # Find Models By Capability
    # ======================================================

    def find_models(
        self,
        capability: str,
    ) -> List[ModelDefinition]:

        models = self.registry.find_by_capability(
            capability
        )

        return sorted(
            models,
            key=lambda model: model.priority
        )

    # ======================================================
    # Policy Provider Order
    # ======================================================

    def _policy_order(
        self,
        capability: str,
    ) -> List[str]:

        return self.policy.providers_for(
            capability
        )

    # ======================================================
    # Policy-aware Model Selection
    # ======================================================

    def select(
        self,
        capability: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[ModelDefinition]:

        # --------------------------------------------------
        # Explicit model override
        # --------------------------------------------------

        if model:

            selected = self.registry.get(
                model
            )

            if selected is None:
                return None

            if not selected.enabled:
                return None

            return selected

        # --------------------------------------------------
        # Explicit provider override
        # --------------------------------------------------

        if provider:

            provider = provider.lower()

            candidates = [
                item
                for item in self.find_models(
                    capability
                )
                if item.provider.lower()
                == provider
            ]

            if not candidates:

                return None

            return candidates[0]

        # --------------------------------------------------
        # Normal policy-based selection
        # --------------------------------------------------

        candidates = self.find_models(
            capability
        )

        if not candidates:

            return None

        provider_order = self._policy_order(
            capability
        )

        # --------------------------------------------------
        # Follow policy preference
        # --------------------------------------------------

        for preferred_provider in provider_order:

            preferred_provider = (
                preferred_provider.lower()
            )

            for candidate in candidates:

                if (
                    candidate.provider.lower()
                    == preferred_provider
                ):

                    return candidate

        # --------------------------------------------------
        # Fallback to priority
        # --------------------------------------------------

        return candidates[0]

    # ======================================================
    # Get All Policy Candidates
    # ======================================================

    def candidates(
        self,
        capability: str,
        provider: Optional[str] = None,
    ) -> List[ModelDefinition]:

        models = self.find_models(
            capability
        )

        # --------------------------------------------------
        # Explicit provider
        # --------------------------------------------------

        if provider:

            provider = provider.lower()

            models = [
                model
                for model in models
                if model.provider.lower()
                == provider
            ]

            return models

        # --------------------------------------------------
        # Policy ordering
        # --------------------------------------------------

        provider_order = self._policy_order(
            capability
        )

        ordered = []

        # --------------------------------------------------
        # Add providers in policy order
        # --------------------------------------------------

        for preferred_provider in provider_order:

            preferred_provider = (
                preferred_provider.lower()
            )

            for model in models:

                if (
                    model.provider.lower()
                    == preferred_provider
                ):

                    ordered.append(model)

        # --------------------------------------------------
        # Add any unlisted providers
        # --------------------------------------------------

        for model in models:

            if model not in ordered:

                ordered.append(model)

        return ordered

    # ======================================================
    # Default Model
    # ======================================================

    def default(
        self,
    ) -> Optional[ModelDefinition]:

        models = self.registry.enabled()

        if not models:

            return None

        return sorted(
            models,
            key=lambda model: model.priority
        )[0]