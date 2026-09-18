import unittest
from unittest.mock import patch

from config import settings
from core.assistant_name import normalize_assistant_invocation
from core.assistant_name import (
    get_assistant_aliases,
    is_current_assistant_name,
    is_legacy_assistant_alias,
)
from core.routers.browser_router import browser_route
from core.routers.greeting_router import greeting_route
from core.routers.system_router import system_route


class AstraRoutingTests(unittest.TestCase):

    def setUp(self):
        self._assistant_name_patch = patch.object(settings, "APP_NAME", "ASTRA")
        self._assistant_name_patch.start()

    def tearDown(self):
        self._assistant_name_patch.stop()

    def test_controlled_assistant_aliases_extract_commands(self):
        cases = (
            ("hey astra", "astra", ""),
            ("hey ashram", "ashram", ""),
            ("astra", "astra", ""),
            ("hey astra what time is it", "astra", "what time is it"),
            ("hey ashram what time is it", "ashram", "what time is it"),
            ("hey ashtra what time is it", "ashtra", "what time is it"),
            ("astra what time is it", "astra", "what time is it"),
            ("hey ashram open chrome", "ashram", "open chrome"),
            (
                "hey ashram search esp32 on google",
                "ashram",
                "search esp32 on google",
            ),
            (
                "hey ashram tell me about esp32",
                "ashram",
                "tell me about esp32",
            ),
            ("hey jarvis what time is it", "jarvis", "what time is it"),
        )

        for text, alias, command in cases:
            with self.subTest(text=text):
                invocation = normalize_assistant_invocation(text)
                self.assertIsNotNone(invocation)
                self.assertEqual(invocation.alias, alias)
                self.assertEqual(invocation.command, command)

    def test_unknown_words_are_not_fuzzy_assistant_aliases(self):
        self.assertIsNone(
            normalize_assistant_invocation("hey astronomy what time is it")
        )

    def test_configured_name_derives_wake_aliases_and_invocations(self):
        with patch.object(settings, "APP_NAME", "MAX"):
            wake_words = settings.get_wake_words()
            self.assertEqual(wake_words[:3], ("max", "hey max", "hello max"))
            self.assertIn("hey jarvis", wake_words)
            self.assertNotIn("hey maxwell", wake_words)

            self.assertEqual(
                get_assistant_aliases(),
                ("max", "ashtra", "ashram", "jarvis"),
            )
            self.assertTrue(is_current_assistant_name("MAX"))
            self.assertTrue(is_legacy_assistant_alias("JARVIS"))

            invocation = normalize_assistant_invocation(
                "hello max search esp32 on google"
            )
            self.assertEqual(invocation.alias, "max")
            self.assertEqual(invocation.command, "search esp32 on google")

            legacy = normalize_assistant_invocation("hey jarvis open chrome")
            self.assertEqual(legacy.command, "open chrome")

    def test_pronunciation_aliases_remain_when_name_changes(self):
        with patch.object(settings, "APP_NAME", "MAX"):
            for phrase in (
                "hey ashtra what time is it",
                "hey ashram what time is it",
                "hey jarvis what time is it",
            ):
                with self.subTest(phrase=phrase):
                    invocation = normalize_assistant_invocation(phrase)
                    self.assertEqual(invocation.command, "what time is it")

    def test_jarvis_can_be_the_current_display_name(self):
        with patch.object(settings, "APP_NAME", "JARVIS"):
            invocation = normalize_assistant_invocation("hey jarvis open chrome")
            self.assertTrue(invocation.is_current_name)
            self.assertTrue(invocation.is_legacy_alias)
            self.assertEqual(invocation.command, "open chrome")

    def test_configured_name_only_uses_existing_greeting_route(self):
        with patch.object(settings, "APP_NAME", "MAX"):
            invocation = normalize_assistant_invocation("max")
            self.assertEqual(invocation.command, "")
            plan = greeting_route("hey max")
            self.assertEqual(plan[0]["action"], "greet")

    def test_name_question_uses_identity_route(self):
        with patch.object(settings, "APP_NAME", "MAX"):
            self.assertEqual(
                greeting_route("what is your name"),
                [{"action": "assistant_name"}],
            )
            self.assertEqual(
                greeting_route("hey max what's your name"),
                [{"action": "assistant_name"}],
            )

    def test_extracted_commands_use_existing_fast_routes(self):
        cases = (
            ("hey astra", greeting_route, "greet"),
            ("hey ashram", greeting_route, "greet"),
            ("astra", greeting_route, "greet"),
            ("hey astra what time is it", system_route, "time"),
            ("hey ashram what time is it", system_route, "time"),
            ("astra what time is it", system_route, "time"),
            ("hey ashram open chrome", browser_route, "open"),
        )

        for text, router, action in cases:
            with self.subTest(text=text):
                invocation = normalize_assistant_invocation(text)
                command = invocation.command or "hey astra"
                plan = router(command)
                self.assertIsNotNone(plan)
                self.assertEqual(plan[0]["action"], action)


if __name__ == "__main__":
    unittest.main()
