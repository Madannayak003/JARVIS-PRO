"""
JARVIS PRO
AI Core - Model Policy

Defines which AI capabilities should prefer
which providers/models.

Policy decides preference.
Router decides availability and fallback.
"""

from typing import Dict, List


class AIModelPolicy:
    """
    Central model-selection policy.
    """

    # ======================================================
    # Provider Preference
    # ======================================================

    PROVIDER_PREFERENCES: Dict[str, List[str]] = {

        # --------------------------------------------------
        # Coding
        # --------------------------------------------------

        "coding": [
            "gemini",
            "openai",
            "ollama",
        ],

        # --------------------------------------------------
        # Developer Mode
        # --------------------------------------------------

        "developer": [
            "gemini",
            "openai",
            "ollama",
        ],

        # --------------------------------------------------
        # Editing
        # --------------------------------------------------

        "editing": [
            "gemini",
            "openai",
            "ollama",
        ],

        # --------------------------------------------------
        # Repair
        # --------------------------------------------------

        "repair": [
            "gemini",
            "openai",
            "ollama",
        ],

        # --------------------------------------------------
        # Reasoning
        # --------------------------------------------------

        "reasoning": [
            "openai",
            "gemini",
            "ollama",
        ],

        # --------------------------------------------------
        # Conversation
        # --------------------------------------------------

        "conversation": [
            "gemini",
            "openai",
            "ollama",
        ],

        # --------------------------------------------------
        # Planning
        # --------------------------------------------------

        "planning": [
            "openai",
            "gemini",
            "ollama",
        ],

        # --------------------------------------------------
        # Memory
        # --------------------------------------------------

        "memory": [
            "gemini",
            "ollama",
        ],

        # --------------------------------------------------
        # Fast
        # --------------------------------------------------

        "fast": [
            "gemini",
            "ollama",
        ],

        # --------------------------------------------------
        # Offline
        # --------------------------------------------------

        "offline": [
            "ollama",
        ],
    }

    # ======================================================
    # Get Provider Preference
    # ======================================================

    @classmethod
    def providers_for(
        cls,
        capability: str,
    ) -> List[str]:

        capability = (
            capability
            .strip()
            .lower()
        )

        return cls.PROVIDER_PREFERENCES.get(
            capability,
            [
                "gemini",
                "openai",
                "ollama",
            ],
        )