"""Focused regression tests for the shared conversational result strategy."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace


MODULE_PATH = (
    Path(__file__).parents[1]
    / "brain"
    / "natural"
    / "response_strategy.py"
)

SPEC = importlib.util.spec_from_file_location(
    "jarvis_response_strategy_under_test",
    MODULE_PATH,
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ResponseStrategyTests(unittest.TestCase):
    def test_message_bearing_results_are_narrated_without_raw_dicts(self):
        self.assertEqual(
            MODULE.action_result_message(
                "open",
                {"app": "Spotify"},
                {"message": "Spotify is open."},
            ),
            "Spotify is open.",
        )
        self.assertEqual(
            MODULE.action_result_message(
                "open",
                {"app": "Spotify"},
                {"error": "Spotify isn't available right now."},
            ),
            "Spotify isn't available right now.",
        )
        self.assertEqual(
            MODULE.action_result_message(
                "open",
                {"app": "Spotify"},
                {"success": True},
            ),
            "Spotify is open.",
        )

    def test_structured_technical_failures_are_normalized(self):
        message = MODULE.action_result_message(
            "search",
            {"query": "Arduino Uno"},
            {
                "success": False,
                "error": "ConnectionError('service refused connection')",
            },
        )

        self.assertEqual(
            message,
            "I couldn't connect to the service. "
            "Check that it is running and try again.",
        )
        self.assertNotIn("ConnectionError", message)
        self.assertNotIn("{'", message)

    def test_successful_open_has_a_natural_fallback(self):
        self.assertEqual(
            MODULE.action_result_message(
                "open",
                {"app": "chrome"},
                {"success": True, "status": "completed"},
            ),
            "Chrome is open.",
        )

    def test_existing_strategy_still_distinguishes_action_and_conversation(self):
        engine = MODULE.ResponseStrategyEngine()

        action = engine.decide(
            SimpleNamespace(
                intent="open_app",
                mode=SimpleNamespace(value="action"),
            )
        )
        conversation = engine.decide(
            SimpleNamespace(
                intent="explain_topic",
                mode=SimpleNamespace(value="conversation"),
            )
        )

        self.assertEqual(action.mode, MODULE.ResponseMode.ACTION)
        self.assertFalse(action.needs_ai)
        self.assertEqual(conversation.mode, MODULE.ResponseMode.CONVERSATION)
        self.assertTrue(conversation.needs_ai)


if __name__ == "__main__":
    unittest.main()
