"""Regression tests for sequential browser search-result follow-ups."""

import unittest

from brain.execution_context import ExecutionContextResolver
from brain.conversation_understanding import ConversationUnderstandingEngine
from brain.followup_execution_bridge import FollowUpExecutionBridge
from brain.followup_resolver import FollowUpResolver
from brain.reference_resolver import ReferenceResolver
from brain.conversation_context import ConversationContextManager
from core.browser_context import BrowserResult, browser_context


class BrowserFollowUpReferenceTests(unittest.TestCase):

    def setUp(self):
        self.execution_context = ExecutionContextResolver()
        self.references = ReferenceResolver()
        self.understanding = ConversationUnderstandingEngine()
        self.follow_up = FollowUpResolver(self.references)
        self.execution_bridge = FollowUpExecutionBridge()
        self.conversation = ConversationContextManager()
        browser_context.clear_search()

    def tearDown(self):
        browser_context.clear_search()

    def record_execution(self, resolved, result=True):
        self.conversation.update(
            application=resolved.application,
            skill=resolved.skill,
            topic=resolved.topic,
            task=resolved.task,
            intent=resolved.intent,
            action=resolved.action,
            object=resolved.object,
            objects=resolved.objects,
            last_result=result,
        )

    def search(self, query, count=6):
        results = [
            BrowserResult(
                title=f"{query} result {index}",
                url=f"https://example.test/{query}/{index}",
                platform="google",
                result_type="search",
            )
            for index in range(1, count + 1)
        ]
        browser_context.set_search(query, "google", results)
        resolved = self.execution_context.resolve(
            "google_search",
            result=True,
        )
        self.record_execution(resolved)
        return results

    def resolve_ordinal(self, phrase):
        result = self.references.resolve(
            phrase,
            self.conversation,
        )
        self.assertTrue(result.resolved, result.reason)
        return result.value

    def open_result(self, result):
        resolved = self.execution_context.resolve(
            "browser_open_result",
            {"url": result.url},
            result=True,
        )
        self.assertIs(resolved.object, result)
        self.assertEqual(resolved.objects, browser_context.last_search_results)
        self.record_execution(resolved)

    def test_sequential_ordinals_keep_the_original_six_result_set(self):
        results = self.search("python")

        for phrase, index in (
            ("the first one", 0),
            ("the second one", 1),
            ("the third one", 2),
            ("the sixth one", 5),
        ):
            selected = self.resolve_ordinal(phrase)
            self.assertIs(selected, results[index])
            self.open_result(selected)
            self.assertEqual(browser_context.last_search_results, results)

    def test_opening_first_result_preserves_open_it_and_remaining_results(self):
        results = self.search("python")

        first = self.resolve_ordinal("the first one")
        self.open_result(first)

        self.assertIs(self.resolve_ordinal("it"), first)
        self.assertIs(self.resolve_ordinal("the second one"), results[1])
        self.assertEqual(len(browser_context.last_search_results), 6)

    def test_follow_up_pipeline_resolves_no_the_and_builds_browser_action(self):
        results = self.search("python")

        first = self.resolve_ordinal("the first one")
        self.open_result(first)

        understanding = self.understanding.understand("Open second one")
        self.assertEqual(understanding.references, ["the second one"])

        follow_up = self.follow_up.resolve(understanding, self.conversation)
        self.assertTrue(follow_up.is_follow_up)
        self.assertIs(
            follow_up.resolved_references["the second one"],
            results[1],
        )

        plan = self.execution_bridge.resolve(
            raw_input="Open second one",
            follow_up=follow_up,
        )
        self.assertEqual(
            plan,
            [{"action": "browser_open_result", "url": results[1].url}],
        )

        sixth_understanding = self.understanding.understand("Open sixth one")
        sixth_follow_up = self.follow_up.resolve(
            sixth_understanding,
            self.conversation,
        )
        self.assertIs(
            sixth_follow_up.resolved_references["the sixth one"],
            results[5],
        )

    def test_new_search_replaces_the_active_reference_collection(self):
        old_results = self.search("python")
        new_results = self.search("esp32")

        self.assertIs(self.resolve_ordinal("the first one"), new_results[0])
        self.assertIsNot(self.resolve_ordinal("the first one"), old_results[0])
        self.assertEqual(browser_context.last_search_query, "esp32")


if __name__ == "__main__":
    unittest.main()
