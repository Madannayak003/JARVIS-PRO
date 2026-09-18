import unittest

from core.assistant_name import normalize_assistant_invocation
from core.routers.browser_router import browser_route
from core.routers.greeting_router import greeting_route
from core.routers.system_router import system_route


class AstraRoutingTests(unittest.TestCase):

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
