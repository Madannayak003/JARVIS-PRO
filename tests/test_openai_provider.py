"""OpenAI-only provider checks.

The two real API tests intentionally use the configured provider/model and do
not mock the OpenAI service. Unit tests below them exercise local error paths
without making additional API calls.
"""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai.core.schemas import AIRequest
from ai.core.registry import ModelRegistry
from ai.providers.openai import OpenAIProvider
from config.environment import load_environment


def _error_category(error):
    text = str(error or "").lower()
    if "authentication" in text or "api key" in text or "401" in text:
        return "authentication"
    if "quota" in text or "billing" in text or "429" in text:
        return "quota/rate-limit"
    if "model" in text and ("not found" in text or "does not exist" in text):
        return "model-unavailable"
    return "api-error"


class OpenAIProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_environment()
        cls.api_key_present = bool(os.getenv("OPENAI_API_KEY"))
        cls.provider = OpenAIProvider()
        print(f"[OPENAI TEST] Provider: {cls.provider.name}")
        print(f"[OPENAI TEST] Model: {cls.provider.model}")
        if not cls.api_key_present:
            raise AssertionError(
                "[OPENAI TEST] OPENAI_API_KEY is missing from the environment."
            )

    def test_real_generate_current_model(self):
        response = self.provider.generate(
            AIRequest(prompt="Reply with exactly: OPENAI_TEST_OK")
        )
        print(f"[OPENAI TEST] Response: {response.text.strip()}")
        if not response.success:
            category = _error_category(response.error)
            print(f"[OPENAI TEST] Status: FAILURE ({category})")
            self.fail(f"OpenAI generate failed: {category}: {response.error}")
        print("[OPENAI TEST] Status: SUCCESS")
        self.assertEqual(response.text.strip(), "OPENAI_TEST_OK")

    def test_real_stream_current_model(self):
        chunks = list(
            self.provider.stream(
                AIRequest(prompt="Reply with exactly: OPENAI_STREAM_OK")
            )
        )
        text = "".join(chunk.text for chunk in chunks).strip()
        print(f"[OPENAI TEST] Stream response: {text}")
        errors = [
            chunk.metadata.get("error")
            for chunk in chunks
            if chunk.metadata.get("success") is False
        ]
        if errors:
            category = _error_category(errors[-1])
            print(f"[OPENAI TEST] Stream status: FAILURE ({category})")
            self.fail(f"OpenAI stream failed: {category}: {errors[-1]}")
        print("[OPENAI TEST] Stream status: SUCCESS")
        self.assertEqual(text, "OPENAI_STREAM_OK")

    def test_missing_api_key_is_reported_without_calling_sdk(self):
        with patch("ai.providers.openai.get_env", return_value=""):
            provider = OpenAIProvider(api_key=None)
            response = provider.generate(AIRequest(prompt="test"))
        self.assertFalse(response.success)
        self.assertIn("OPENAI_API_KEY", response.error)

    def test_configured_openai_model_is_enabled(self):
        model = next(
            model
            for model in ModelRegistry().all()
            if model.provider == "openai"
        )
        self.assertEqual(model.name, self.provider.model)
        self.assertTrue(model.enabled)

    def test_generate_preserves_jarvis_response_interface(self):
        provider = OpenAIProvider(api_key="test-key")
        provider._client = Mock()
        provider._client.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="OPENAI_GENERATE_OK")
                )
            ]
        )
        response = provider.generate(AIRequest(prompt="test"))
        self.assertTrue(response.success)
        self.assertEqual(response.text, "OPENAI_GENERATE_OK")
        self.assertEqual(response.provider, "openai")

    def test_stream_preserves_jarvis_stream_interface(self):
        provider = OpenAIProvider(api_key="test-key")
        provider._client = Mock()
        provider._client.chat.completions.create.return_value = iter(
            [
                SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            delta=SimpleNamespace(content="OPENAI_")
                        )
                    ]
                ),
                SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            delta=SimpleNamespace(content="STREAM_OK")
                        )
                    ]
                ),
            ]
        )
        chunks = list(provider.stream(AIRequest(prompt="test")))
        self.assertEqual("".join(chunk.text for chunk in chunks), "OPENAI_STREAM_OK")
        self.assertTrue(chunks[-1].done)
        self.assertTrue(chunks[-1].metadata["success"])

    def test_api_exception_is_returned_as_provider_error(self):
        provider = OpenAIProvider(api_key="test-key")
        provider._client = Mock()
        provider._client.chat.completions.create.side_effect = RuntimeError(
            "simulated OpenAI API failure"
        )
        response = provider.generate(AIRequest(prompt="test"))
        self.assertFalse(response.success)
        self.assertEqual(response.metadata["error_type"], "RuntimeError")
        self.assertIn("simulated OpenAI API failure", response.error)

    def test_stream_api_exception_is_returned_without_secret_data(self):
        provider = OpenAIProvider(api_key="secret-test-key")
        provider._client = Mock()
        provider._client.chat.completions.create.side_effect = RuntimeError(
            "simulated OpenAI stream failure"
        )
        chunks = list(provider.stream(AIRequest(prompt="test")))
        self.assertEqual(len(chunks), 1)
        self.assertFalse(chunks[0].metadata["success"])
        self.assertNotIn("secret-test-key", str(chunks[0].metadata))


if __name__ == "__main__":
    unittest.main()
