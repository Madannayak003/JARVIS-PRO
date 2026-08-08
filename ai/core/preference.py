"""
JARVIS PRO
AI Core - AI Preference

Stores the user's temporary AI provider/model preference.

Examples:
    use Gemini
    use GPT
    use Ollama
    use Qwen
    auto mode
"""


class AIPreference:

    def __init__(self):

        self.provider = None
        self.model = None

    # ======================================================
    # Set Provider
    # ======================================================

    def set_provider(
        self,
        provider: str,
    ):

        self.provider = (
            provider.strip().lower()
        )

        self.model = None

    # ======================================================
    # Set Model
    # ======================================================

    def set_model(
        self,
        model: str,
    ):

        self.model = (
            model.strip()
        )

        self.provider = None

    # ======================================================
    # Automatic Mode
    # ======================================================

    def clear(self):

        self.provider = None
        self.model = None

    # ======================================================
    # State
    # ======================================================

    @property
    def is_manual(self) -> bool:

        return (
            self.provider is not None
            or self.model is not None
        )

    # ======================================================
    # Description
    # ======================================================

    def describe(self) -> str:

        if self.model:

            return (
                f"model:{self.model}"
            )

        if self.provider:

            return (
                f"provider:{self.provider}"
            )

        return "auto"