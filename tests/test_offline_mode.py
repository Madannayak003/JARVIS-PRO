"""Focused tests for the offline provider/action integration."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from ai.core.schemas import AIResponse
from voice.offline.offline_action_bridge import OfflineActionBridge, OfflineRoute
from voice.offline.offline_runner import process_command


class OfflineActionBridgeTests(unittest.TestCase):
    def test_local_commands_are_routed_without_ai(self):
        bridge = OfflineActionBridge()

        with patch(
            "voice.offline.offline_action_bridge.execute_ai_plan",
            return_value=[True],
        ) as execute:
            result = bridge.handle("open calculator")

        self.assertEqual(result.route, OfflineRoute.LOCAL_ACTION)
        self.assertEqual(result.plan[0]["action"], "open")
        execute.assert_called_once()

    def test_network_commands_are_blocked_before_execution(self):
        bridge = OfflineActionBridge()

        with patch(
            "voice.offline.offline_action_bridge.execute_ai_plan"
        ) as execute:
            result = bridge.handle("search Google for ESP32")

        self.assertEqual(result.route, OfflineRoute.NETWORK_REQUIRED)
        execute.assert_not_called()
        self.assertIn("internet", result.message.lower())

    def test_conversation_is_not_sent_to_action_executor(self):
        bridge = OfflineActionBridge()
        result = bridge.classify("tell me about ESP32")
        self.assertEqual(result.route, OfflineRoute.CONVERSATION)

    def test_greeting_uses_existing_local_greeting_action(self):
        bridge = OfflineActionBridge()
        result = bridge.classify("Hey Jarvis.")
        self.assertEqual(result.route, OfflineRoute.LOCAL_ACTION)
        self.assertEqual(result.plan[0]["action"], "greet")


class OfflineCommandTests(unittest.TestCase):
    def test_conversation_reaches_ollama_adapter(self):
        class FakeAI:
            def ask(self, text):
                self.received = text
                return "Local answer."

        ai = FakeAI()
        bridge = OfflineActionBridge()

        with patch("voice.offline.offline_runner.HUDAdapter.response"):
            response = process_command("tell me about ESP32", ai=ai, bridge=bridge)

        self.assertEqual(response, "Local answer.")
        self.assertEqual(ai.received, "tell me about ESP32")

    def test_local_command_does_not_call_ai(self):
        class FailingAI:
            def ask(self, text):
                raise AssertionError("local action called Ollama")

        bridge = OfflineActionBridge()
        with patch(
            "voice.offline.offline_action_bridge.execute_ai_plan",
            return_value=[True],
        ), patch("voice.offline.offline_runner.HUDAdapter.response"):
            response = process_command(
                "open notepad",
                ai=FailingAI(),
                bridge=bridge,
            )

        self.assertEqual(response, "Done.")


class OfflineAIProviderTests(unittest.TestCase):
    def test_offline_ai_uses_local_ollama_provider_once(self):
        from voice.offline.offline_ai import OfflineAI

        class FakeProvider:
            def __init__(self):
                self.availability_checks = 0
                self.generations = 0

            def is_available(self):
                self.availability_checks += 1
                return True

            def generate(self, request):
                self.generations += 1
                return AIResponse(
                    text="Local answer.",
                    provider="ollama",
                    model=request.model,
                    success=True,
                )

        provider = FakeProvider()
        ai = OfflineAI(provider=provider)
        self.assertTrue(ai.ready)
        self.assertEqual(provider.availability_checks, 1)
        self.assertEqual(ai.ask("what is ESP32"), "Local answer.")
        self.assertEqual(provider.generations, 1)


if __name__ == "__main__":
    unittest.main()
