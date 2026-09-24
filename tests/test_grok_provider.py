import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai.core.schemas import AIRequest
from ai.providers.grok import GrokProvider


class GrokProviderTests(unittest.TestCase):
    def test_missing_key_is_cleanly_unavailable(self):
        with patch("ai.providers.grok.get_env", return_value=""):
            provider = GrokProvider()
        self.assertFalse(provider.is_available())
        response = provider.generate(AIRequest(prompt="test"))
        self.assertFalse(response.success)
        self.assertIn("XAI_API_KEY", response.error)

    def test_uses_xai_base_url_and_default_model(self):
        with patch("ai.providers.grok.OpenAI") as openai:
            provider = GrokProvider(api_key="test-key")
            client = Mock()
            client.chat.completions.create.return_value = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
            )
            openai.return_value = client

            response = provider.generate(AIRequest(prompt="test"))

        self.assertTrue(response.success)
        self.assertEqual(provider.name, "grok")
        self.assertEqual(provider.model, "grok-4.7")
        self.assertEqual(openai.call_args.kwargs["base_url"], "https://api.x.ai/v1")
        self.assertEqual(
            openai.call_args.kwargs["api_key"],
            "test-key",
        )
        self.assertEqual(
            client.chat.completions.create.call_args.kwargs["model"],
            "grok-4.7",
        )

    def test_stream_uses_normalized_stream_interface(self):
        provider = GrokProvider(api_key="secret-test-key")
        provider._client = Mock()
        provider._client.chat.completions.create.return_value = iter(
            [
                SimpleNamespace(
                    choices=[SimpleNamespace(delta=SimpleNamespace(content="GROK_"))]
                ),
                SimpleNamespace(
                    choices=[SimpleNamespace(delta=SimpleNamespace(content="OK"))]
                ),
            ]
        )

        chunks = list(provider.stream(AIRequest(prompt="test")))
        self.assertEqual("".join(chunk.text for chunk in chunks), "GROK_OK")
        self.assertTrue(chunks[-1].done)
        self.assertTrue(chunks[-1].metadata["success"])
        self.assertNotIn("secret-test-key", str(chunks))


if __name__ == "__main__":
    unittest.main()
