import unittest
from unittest.mock import patch

from ai.core.preference import AIPreference
from ai.core.router import AIRouter
from ai.core.schemas import AIRequest, AIResponse
from ai.providers.base import AIProvider


class FakeProvider(AIProvider):
    def __init__(self, provider, outcomes, available=True):
        self._name = provider
        self.outcomes = list(outcomes)
        self.available = available
        self.calls = 0

    @property
    def name(self):
        return self._name

    def is_available(self):
        return self.available

    def generate(self, request):
        self.calls += 1
        success, text = self.outcomes.pop(0)
        return AIResponse(
            text=text if success else "",
            provider=self.name,
            model=request.model or "test-model",
            success=success,
            error=None if success else f"{self.name} failed",
        )

    def stream(self, request):
        raise NotImplementedError


def make_router(outcomes, selected=None):
    router = AIRouter()
    providers = {
        name: FakeProvider(name, outcomes.get(name, [(False, "failed")]))
        for name in ("gemini", "grok", "openai", "ollama")
    }
    for provider in providers.values():
        router.register_provider(provider)
    request = AIRequest(prompt="test", capability="conversation", provider=selected)
    return router, providers, request


class AIProviderSelectionTests(unittest.TestCase):
    def test_auto_order_is_gemini_grok_openai_ollama(self):
        router, providers, request = make_router(
            {
                "gemini": [(False, "failed")],
                "grok": [(False, "failed")],
                "openai": [(False, "failed")],
                "ollama": [(True, "ollama ok")],
            }
        )
        response = router.generate(request)
        self.assertTrue(response.success)
        self.assertEqual(response.provider, "ollama")
        self.assertEqual(
            [name for name, provider in providers.items() if provider.calls],
            ["gemini", "grok", "openai", "ollama"],
        )

    def test_auto_stops_at_first_success(self):
        router, providers, request = make_router(
            {
                "gemini": [(True, "gemini ok")],
                "grok": [(True, "grok should not run")],
                "openai": [(True, "openai should not run")],
                "ollama": [(True, "ollama should not run")],
            }
        )
        response = router.generate(request)
        self.assertEqual(response.provider, "gemini")
        self.assertEqual(providers["grok"].calls, 0)

    def test_manual_provider_does_not_fallback(self):
        router, providers, request = make_router(
            {
                "gemini": [(False, "failed")],
                "grok": [(True, "grok should not run")],
                "openai": [(True, "openai should not run")],
                "ollama": [(True, "ollama should not run")],
            },
            selected="gemini",
        )
        response = router.generate(request)
        self.assertFalse(response.success)
        self.assertEqual(providers["grok"].calls, 0)
        self.assertEqual(providers["openai"].calls, 0)
        self.assertEqual(providers["ollama"].calls, 0)

    def test_preference_modes_default_to_auto_and_persist(self):
        with patch("ai.core.preference.get_ai_provider_setting", return_value="AUTO"), \
             patch("ai.core.preference.set_ai_provider_setting") as save:
            preference = AIPreference()
            self.assertEqual(preference.mode, "auto")
            preference.set_provider("GROK")
            self.assertEqual(preference.mode, "grok")
            save.assert_called_once_with("grok")


if __name__ == "__main__":
    unittest.main()
