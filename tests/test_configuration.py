"""Focused tests for JARVIS environment-backed configuration."""

from __future__ import annotations

import importlib
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from config.environment import load_environment
from config import personal_links
from config import settings
from ai.providers.gemini import GeminiProvider
from ai.providers.ollama import OllamaProvider
from ai.providers.openai import OpenAIProvider


class ConfigurationTests(unittest.TestCase):
    def test_dotenv_loads_without_overriding_process_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "JARVIS_TEST_CONFIG=loaded\n"
                "JARVIS_TEST_EXISTING=from-file\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {"JARVIS_TEST_EXISTING": "from-process"},
                clear=False,
            ):
                os.environ.pop("JARVIS_TEST_CONFIG", None)
                load_environment(env_file)
                self.assertEqual(os.environ["JARVIS_TEST_CONFIG"], "loaded")
                self.assertEqual(
                    os.environ["JARVIS_TEST_EXISTING"],
                    "from-process",
                )

            os.environ.pop("JARVIS_TEST_CONFIG", None)
            os.environ.pop("JARVIS_TEST_EXISTING", None)

    def test_personal_links_api_remains_compatible(self):
        values = {
            "PERSONAL_GITHUB_URL": "https://example.test/github",
            "PERSONAL_PORTFOLIO_URL": "https://example.test/portfolio",
            "IOTRIX_LAB_URL": "https://example.test/iotrix",
            "JARVIS_REPOSITORY_URL": "https://example.test/jarvis",
            "SMART_PARKING_URL": "",
        }
        with patch.dict(os.environ, values, clear=False):
            module = importlib.reload(personal_links)
            self.assertEqual(module.get_link("github"), values["PERSONAL_GITHUB_URL"])
            self.assertEqual(module.get_link("portfolio"), values["PERSONAL_PORTFOLIO_URL"])
            self.assertEqual(module.get_link("iotrix_lab"), values["IOTRIX_LAB_URL"])
            self.assertEqual(module.get_link("jarvis_repository"), values["JARVIS_REPOSITORY_URL"])
            self.assertTrue(module.has_link("github"))
            self.assertFalse(module.has_link("smart_parking"))
            self.assertFalse(module.has_link("missing"))

        importlib.reload(personal_links)

    def test_optional_defaults_are_preserved(self):
        with patch.dict(os.environ, {"OLLAMA_API_URL": ""}, clear=False):
            self.assertEqual(
                importlib.reload(settings).OLLAMA_URL,
                "http://localhost:11434/api/generate",
            )
            self.assertEqual(
                OllamaProvider().url,
                "http://127.0.0.1:11434/api/generate",
            )

    def test_ollama_api_url_uses_explicit_environment_value(self):
        value = "http://ollama.example.test:11434/api/generate"
        with patch.dict(os.environ, {"OLLAMA_API_URL": value}, clear=False):
            self.assertEqual(OllamaProvider().url, value)

    def test_openai_api_key_uses_environment_fallback(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}, clear=False):
            self.assertEqual(OpenAIProvider().api_key, "test-openai-key")

    def test_youtube_api_key_uses_environment_fallback(self):
        from config import youtube

        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test-youtube-key"}, clear=False):
            module = importlib.reload(youtube)
            self.assertEqual(module.YOUTUBE_API_KEY, "test-youtube-key")

        importlib.reload(youtube)

    def test_live_model_uses_explicit_environment_value_and_default(self):
        from voice import live_conversation

        with patch.dict(os.environ, {"JARVIS_LIVE_MODEL": "test-live-model"}, clear=False):
            module = importlib.reload(live_conversation)
            self.assertEqual(module.LIVE_MODEL, "test-live-model")

        with patch.dict(os.environ, {"JARVIS_LIVE_MODEL": ""}, clear=False):
            module = importlib.reload(live_conversation)
            self.assertEqual(module.LIVE_MODEL, module.DEFAULT_MODEL)

        importlib.reload(live_conversation)

    def test_gemini_api_key_uses_environment_fallback(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-gemini-key"}, clear=False):
            self.assertEqual(GeminiProvider().api_key, "test-gemini-key")

    def test_gemini_initialization_does_not_print_api_key(self):
        output = io.StringIO()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-gemini-key"}, clear=False):
            with redirect_stdout(output):
                GeminiProvider()
        self.assertNotIn("test-gemini-key", output.getvalue())

    def test_example_has_no_secret_shaped_values(self):
        example = (Path(__file__).parents[1] / ".env.example").read_text(
            encoding="utf-8"
        )
        self.assertIn("GEMINI_API_KEY=your_gemini_api_key_here", example)
        self.assertNotRegex(example, r"(?i)(client_secret|api_key|token)=([0-9a-f]{32,}|sk-[A-Za-z0-9_-]+)")


if __name__ == "__main__":
    unittest.main()
