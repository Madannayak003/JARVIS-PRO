import unittest
from threading import Event
from types import SimpleNamespace
from unittest.mock import patch

from config import settings
from brain.conversation_coordinator import (
    ConversationCoordinator,
    conversation_coordinator,
)
from core.core_state import mark_core_ready


class ClarificationFlowTests(unittest.TestCase):

    def test_answers_preserve_context_and_clear_pending_state(self):
        cases = (
            ("esp32", "search on google", "esp32 search on google"),
            ("edit a file", "main.py", "edit a file main.py"),
            ("continue the task", "yes", "continue the task yes"),
            ("build hardware", "Arduino Uno", "build hardware Arduino Uno"),
            (
                "schedule a backup",
                "tomorrow morning after work",
                "schedule a backup tomorrow morning after work",
            ),
        )

        for task, answer, expected in cases:
            with self.subTest(answer=answer):
                coordinator = ConversationCoordinator()
                coordinator.start_clarification(
                    field="value",
                    question="What information is needed?",
                    task=task,
                    owner="planner",
                )

                before = coordinator.context.snapshot()
                self.assertEqual(before["pending_question"], "What information is needed?")
                self.assertEqual(before["pending_clarification"], "value")

                result = coordinator.consume_clarification_reply(answer)

                self.assertEqual(result["status"], "resolved")
                self.assertEqual(result["merged_request"], expected)
                self.assertFalse(coordinator.clarification.is_waiting())
                after = coordinator.context.snapshot()
                self.assertIsNone(after["pending_question"])
                self.assertIsNone(after["pending_clarification"])

    def test_explicit_new_command_and_multiple_turns(self):
        coordinator = ConversationCoordinator()
        coordinator.start_clarification("one", "First?", "configure")

        self.assertEqual(
            coordinator.consume_clarification_reply("new command: open calculator"),
            {"status": "new_request"},
        )
        self.assertTrue(coordinator.clarification.is_waiting())

        self.assertEqual(
            coordinator.consume_clarification_reply("alpha")["status"],
            "resolved",
        )
        coordinator.start_clarification("two", "Second?", "configure alpha")
        result = coordinator.consume_clarification_reply("beta")
        self.assertEqual(result["merged_request"], "configure alpha beta")

    def test_search_platform_reply_does_not_recreate_clarification(self):
        coordinator = ConversationCoordinator()
        coordinator.start_clarification(
            field="clarification",
            question="Where would you like me to search?",
            task="search arduino uno",
            metadata={
                "pending_search": "arduino uno",
                "accepted_answers": ["google", "youtube", "github", "chatgpt"],
            },
        )

        result = coordinator.consume_clarification_reply("google")

        self.assertEqual(result["status"], "resolved")
        self.assertEqual(
            result["merged_request"],
            "search arduino uno on google",
        )
        self.assertFalse(coordinator.clarification.is_waiting())

        from ai.planner import create_plan

        self.assertEqual(
            create_plan(result["merged_request"], Event()),
            [{"action": "google_search", "query": "arduino uno"}],
        )

    def test_empty_clarification_input_is_ignored_and_cleared(self):
        for empty_input in (None, "", "   "):
            with self.subTest(empty_input=empty_input):
                coordinator = ConversationCoordinator()
                coordinator.start_clarification(
                    field="action",
                    question="What would you like me to do with esp32?",
                    task="esp32",
                )

                result = coordinator.consume_clarification_reply(empty_input)

                self.assertEqual(result["status"], "empty")
                self.assertFalse(coordinator.clarification.is_waiting())
                snapshot = coordinator.context.snapshot()
                self.assertIsNone(snapshot["pending_question"])
                self.assertIsNone(snapshot["pending_clarification"])

    def test_short_clarification_answers_remain_valid(self):
        for answer in ("Google", "GitHub", "yes"):
            with self.subTest(answer=answer):
                coordinator = ConversationCoordinator()
                coordinator.start_clarification(
                    field="action",
                    question="What would you like me to do with esp32?",
                    task="esp32",
                )

                result = coordinator.consume_clarification_reply(answer)

                self.assertEqual(result["status"], "resolved")
                self.assertTrue(result["merged_request"].endswith(answer))

    def test_dispatcher_drops_empty_clarification_input(self):
        import core.dispatcher as dispatcher

        mark_core_ready()
        conversation_coordinator.clear()
        conversation_coordinator.start_clarification(
            field="action",
            question="What would you like me to do with esp32?",
            task="esp32",
        )

        with patch.object(dispatcher.task_manager, "start") as start:
            dispatcher.dispatch(None)

        start.assert_not_called()
        self.assertFalse(conversation_coordinator.clarification.is_waiting())

    def test_invalid_structured_reply_becomes_a_new_request(self):
        coordinator = ConversationCoordinator()
        coordinator.start_clarification(
            field="platform",
            question="Where should I search?",
            task="search arduino uno",
            metadata={
                "pending_search": "arduino uno",
                "accepted_answers": ["google", "youtube"],
            },
        )

        self.assertEqual(
            coordinator.consume_clarification_reply("shutdown"),
            {"status": "new_request"},
        )
        self.assertFalse(coordinator.clarification.is_waiting())

    def test_executor_preserves_original_request_for_clarify_action(self):
        import core.executor as executor

        with patch.object(executor, "execute") as execute:
            executor.execute_ai_plan(
                [{"action": "clarify", "question": "What action?"}],
                stop_event=None,
                original_request="esp32",
            )

        action, step = execute.call_args.args
        self.assertEqual(action, "clarify")
        self.assertEqual(step["original_request"], "esp32")

    def test_clarify_action_persists_global_coordinator_state(self):
        from skills.ai import clarify

        conversation_coordinator.clear()
        with patch.object(clarify, "speak"):
            self.assertTrue(
                clarify.ai_clarify(
                    {
                        "question": "What would you like me to do with esp32?",
                        "original_request": "esp32",
                    }
                )
            )

        snapshot = conversation_coordinator.context.snapshot()
        self.assertEqual(
            snapshot["pending_question"],
            "What would you like me to do with esp32?",
        )
        self.assertEqual(snapshot["pending_clarification"], "clarification")
        self.assertTrue(conversation_coordinator.clarification.is_waiting())

    def test_dispatcher_consumes_answer_before_normal_routing(self):
        import core.dispatcher as dispatcher

        mark_core_ready()
        conversation_coordinator.clear()
        conversation_coordinator.start_clarification(
            field="action",
            question="What would you like me to do with esp32?",
            task="esp32",
            owner="planner",
        )

        with patch.object(dispatcher.task_manager, "start") as start:
            dispatcher.dispatch("search on google")

        start.assert_called_once_with(
            "planner",
            dispatcher.planner_worker,
            "esp32 search on google",
        )
        snapshot = conversation_coordinator.context.snapshot()
        self.assertIsNone(snapshot["pending_question"])
        self.assertIsNone(snapshot["pending_clarification"])

    def test_dispatcher_clears_stale_state_for_an_explicit_new_command(self):
        import core.dispatcher as dispatcher

        mark_core_ready()
        conversation_coordinator.clear()
        conversation_coordinator.start_clarification(
            field="value",
            question="Which value?",
            task="configure feature",
        )

        with (
            patch.object(dispatcher, "fast_route", return_value=None),
            patch.object(dispatcher, "detect", return_value="planner"),
            patch.object(dispatcher.task_manager, "start") as start,
        ):
            dispatcher.dispatch("new command: open calculator")

        self.assertTrue(start.called)
        self.assertFalse(conversation_coordinator.clarification.is_waiting())
        snapshot = conversation_coordinator.context.snapshot()
        self.assertIsNone(snapshot["pending_question"])
        self.assertIsNone(snapshot["pending_clarification"])

    def test_current_assistant_invocation_preempts_pending_clarification(self):
        import core.dispatcher as dispatcher

        mark_core_ready()
        conversation_coordinator.clear()

        with patch.object(
            settings,
            "APP_NAME",
            "MAX",
        ):
            conversation_coordinator.start_clarification(
                field="action",
                question="What would you like me to do with hey max?",
                task="hey max",
            )

            with (
                patch.object(dispatcher, "fast_route") as fast_route,
                patch.object(dispatcher, "execute") as execute,
            ):
                fast_route.return_value = [
                    {"action": "greet", "command": "hey"}
                ]
                dispatcher.dispatch("hey max")

            fast_route.assert_called_once_with("hey")
            execute.assert_called_once_with(
                "greet",
                {"action": "greet", "command": "hey"},
            )
            self.assertFalse(
                conversation_coordinator.clarification.is_waiting()
            )

    def test_stop_cancels_only_pending_clarification(self):
        from brain.conversation_context import conversation_context

        conversation_coordinator.clear()
        conversation_coordinator.start_clarification(
            field="action",
            question="What would you like me to do with hey max?",
            task="hey max",
        )
        conversation_context.set_user_input("hey max")

        conversation_coordinator.cancel_clarification()

        self.assertFalse(conversation_coordinator.clarification.is_waiting())
        snapshot = conversation_coordinator.context.snapshot()
        self.assertIsNone(snapshot["pending_question"])
        self.assertIsNone(snapshot["pending_clarification"])

    def test_stop_then_changed_name_invocation_is_fresh(self):
        from core.assistant_name import normalize_assistant_invocation
        from core.routers.greeting_router import greeting_route

        conversation_coordinator.clear()
        with patch.object(settings, "APP_NAME", "MAX"):
            conversation_coordinator.start_clarification(
                field="action",
                question="What would you like me to do with hey max?",
                task="hey max",
            )
            self.assertTrue(
                conversation_coordinator.cancel_clarification()
            )

        with patch.object(settings, "APP_NAME", "__ASSISTANT_NAME__"):
            invocation = normalize_assistant_invocation("hey __ASSISTANT_NAME__")
            self.assertEqual(invocation.command, "")
            self.assertEqual(
                greeting_route("hey __ASSISTANT_NAME__"),
                [{"action": "greet", "command": "hey"}],
            )
            self.assertFalse(
                conversation_coordinator.clarification.is_waiting()
            )

    def test_normal_input_reaches_planner_instead_of_broad_memory(self):
        import core.dispatcher as dispatcher

        mark_core_ready()
        conversation_coordinator.clear()
        request = SimpleNamespace(
            relation="new_request",
            intent="command",
            user_input="esp32",
            application=None,
            skill=None,
            topic=None,
            task=None,
            action=None,
            object=None,
            references=[],
            reference=None,
            resolved_references={},
            unresolved_references=[],
            confidence=1.0,
        )

        with (
            patch.object(dispatcher, "fast_route", return_value=None),
            patch.object(dispatcher, "detect", return_value="planner"),
            patch.object(
                dispatcher,
                "learn_explicit_memory",
                return_value={"saved": False},
            ) as learn_memory,
            patch.object(dispatcher.task_manager, "start") as start,
        ):
            dispatcher.dispatch("esp32", conversation_request=request)

        learn_memory.assert_called_once_with("esp32")
        start.assert_called_once_with(
            "planner",
            dispatcher.planner_worker,
            "esp32",
        )

    def test_explicit_rule_memory_still_uses_existing_memory_handler(self):
        from ai.memory_manager import learn

        result = learn("my name is Madan")

        self.assertTrue(
            result.get("saved") or result.get("already_known")
        )


if __name__ == "__main__":
    unittest.main()
