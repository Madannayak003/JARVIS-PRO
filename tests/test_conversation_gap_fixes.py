"""Deterministic coverage for conversational continuity and speech state."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path


# * Load only the dependency-light conversational modules. Importing the normal
# * ``brain`` package initializes optional provider integrations, which this
# * deterministic test does not need and should not mask in the full report.
ROOT = Path(__file__).parents[1]
_MODULE_NAMES = [
    "brain",
    "brain.conversation_context",
    "brain.conversation_understanding",
    "brain.reference_resolver",
    "brain.followup_resolver",
    "brain.followup_execution_bridge",
    "brain.natural",
    "brain.natural.interaction_mode",
    "brain.natural.interaction_decision",
    "brain.natural.natural_context",
    "brain.natural.interaction_classifier",
    "brain.natural.meaning_understanding",
    "brain.natural.response_strategy",
    "brain.natural.conversation_request",
    "brain.natural.natural_pipeline",
    "brain.natural.natural_bridge",
    "jarvis_test_ai_pipeline",
]
_ORIGINAL_MODULES = {
    name: sys.modules[name]
    for name in _MODULE_NAMES
    if name in sys.modules
}

brain_package = types.ModuleType("brain")
brain_package.__path__ = [str(ROOT / "brain")]
natural_package = types.ModuleType("brain.natural")
natural_package.__path__ = [str(ROOT / "brain" / "natural")]
sys.modules["brain"] = brain_package
sys.modules["brain.natural"] = natural_package


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


for _name, _relative_path in (
    ("brain.conversation_context", "brain/conversation_context.py"),
    (
        "brain.conversation_understanding",
        "brain/conversation_understanding.py",
    ),
    ("brain.reference_resolver", "brain/reference_resolver.py"),
    ("brain.followup_resolver", "brain/followup_resolver.py"),
    (
        "brain.followup_execution_bridge",
        "brain/followup_execution_bridge.py",
    ),
    ("brain.natural.interaction_mode", "brain/natural/interaction_mode.py"),
    (
        "brain.natural.interaction_decision",
        "brain/natural/interaction_decision.py",
    ),
    (
        "brain.natural.natural_context",
        "brain/natural/natural_context.py",
    ),
    (
        "brain.natural.interaction_classifier",
        "brain/natural/interaction_classifier.py",
    ),
    (
        "brain.natural.meaning_understanding",
        "brain/natural/meaning_understanding.py",
    ),
    (
        "brain.natural.response_strategy",
        "brain/natural/response_strategy.py",
    ),
    (
        "brain.natural.conversation_request",
        "brain/natural/conversation_request.py",
    ),
    (
        "brain.natural.natural_pipeline",
        "brain/natural/natural_pipeline.py",
    ),
    (
        "brain.natural.natural_bridge",
        "brain/natural/natural_bridge.py",
    ),
    ("jarvis_test_ai_pipeline", "brain/ai_pipeline.py"),
):
    _load_module(_name, ROOT / _relative_path)


from brain.conversation_context import ConversationContextManager
from brain.conversation_understanding import ConversationUnderstandingEngine
from brain.followup_execution_bridge import FollowUpExecutionBridge
from brain.followup_resolver import FollowUpResolver
from brain.natural.interaction_classifier import InteractionClassifier
from brain.natural.natural_context import NaturalContext
from brain.natural.natural_bridge import NaturalConversationBridge
from jarvis_test_ai_pipeline import AIPipeline
from voice.state import (
    cancel_current,
    create_session,
    current_session,
    is_cancelled,
    is_current,
)


for _name in reversed(_MODULE_NAMES):
    if _name in _ORIGINAL_MODULES:
        sys.modules[_name] = _ORIGINAL_MODULES[_name]
    else:
        sys.modules.pop(_name, None)


class ConversationGapFixTests(unittest.TestCase):
    class _Conversation:
        def __init__(self):
            self.users = []
            self.assistants = []

        def add_user_message(self, text):
            self.users.append(text)

        def add_assistant_message(self, text):
            self.assistants.append(text)

    class _ContextBuilder:
        def build(self, user_input):
            return {"user_input": user_input}

    class _PromptBuilder:
        def build(self, context):
            return context["user_input"]

    def test_completed_stream_is_saved_as_one_assistant_turn(self):
        conversation = self._Conversation()
        pipeline = AIPipeline(
            conversation_manager=conversation,
            profile_manager=None,
            context_builder=self._ContextBuilder(),
            prompt_builder=self._PromptBuilder(),
        )

        def stream_callback(system_prompt, prompt, stop_event):
            yield {"response": "Python decorators "}
            yield {"response": "wrap behavior."}

        recorded = []
        fake_brain = types.ModuleType("brain")
        fake_brain.__path__ = []
        fake_coordinator = types.ModuleType(
            "brain.conversation_coordinator"
        )
        fake_coordinator.conversation_coordinator = types.SimpleNamespace(
            record_response=recorded.append,
        )
        previous_brain = sys.modules.get("brain")
        previous_coordinator = sys.modules.get(
            "brain.conversation_coordinator"
        )
        sys.modules["brain"] = fake_brain
        sys.modules["brain.conversation_coordinator"] = fake_coordinator
        try:
            output = list(
                pipeline.process_stream(
                    "Give me an example.",
                    stream_callback,
                    "system",
                )
            )
        finally:
            if previous_brain is None:
                sys.modules.pop("brain", None)
            else:
                sys.modules["brain"] = previous_brain
            if previous_coordinator is None:
                sys.modules.pop("brain.conversation_coordinator", None)
            else:
                sys.modules["brain.conversation_coordinator"] = (
                    previous_coordinator
                )

        self.assertEqual(len(conversation.users), 1)
        self.assertEqual(len(conversation.assistants), 1)
        self.assertEqual(
            conversation.assistants,
            ["Python decorators wrap behavior."],
        )
        self.assertEqual(
            recorded,
            ["Python decorators wrap behavior."],
        )
        self.assertEqual(len(output), 2)

    def test_cancelled_or_failed_stream_is_not_saved_as_completed_reply(self):
        conversation = self._Conversation()
        pipeline = AIPipeline(
            conversation_manager=conversation,
            profile_manager=None,
            context_builder=self._ContextBuilder(),
            prompt_builder=self._PromptBuilder(),
        )

        def interrupted_stream(system_prompt, prompt, stop_event):
            yield {"response": "An incomplete answer"}

        generator = pipeline.process_stream(
            "Give me an example.",
            interrupted_stream,
            "system",
        )
        next(generator)
        generator.close()

        self.assertEqual(conversation.assistants, [])

        def failed_stream(system_prompt, prompt, stop_event):
            yield {"response": "A partial answer"}
            raise RuntimeError("provider failed")

        with self.assertRaises(RuntimeError):
            list(
                pipeline.process_stream(
                    "Give me another example.",
                    failed_stream,
                    "system",
                )
            )

        self.assertEqual(conversation.assistants, [])

    def test_recent_answer_keeps_informational_follow_up_conversational(self):
        previous = {
            "last_user_input": "Tell me about Python decorators.",
            "last_assistant_response": (
                "Python decorators wrap a function or class."
            ),
        }

        for follow_up in (
            "Give me an example.",
            "Give me one simple example.",
            "Show me one.",
            "How does that work?",
            "Show me another one.",
            "What if I want arguments?",
            "What about class decorators?",
        ):
            with self.subTest(follow_up=follow_up):
                context = NaturalContext(
                    user_input=follow_up,
                    conversation=previous,
                )
                decision = InteractionClassifier().classify(context)

                self.assertEqual(decision.mode.value, "conversation")
                self.assertFalse(decision.requires_action)

    def test_multi_subject_bare_example_remains_conservative(self):
        context = NaturalContext(
            user_input="Give me an example.",
            conversation={
                "last_user_input": (
                    "Explain Python decorators and JavaScript closures."
                ),
                "last_assistant_response": "Both are useful abstractions.",
            },
        )

        decision = InteractionClassifier().classify(context)

        self.assertNotEqual(decision.intent, "contextual_conversation")

    def test_contextual_example_becomes_follow_up_request_for_chat(self):
        class _Message:
            def __init__(self, role, content):
                self.role = role
                self.content = content

        class _Conversation:
            def get_recent_messages(self, limit=10):
                return [
                    _Message("user", "What is Python?"),
                    _Message(
                        "assistant",
                        "Python is a programming language.",
                    ),
                ]

        context = ConversationContextManager()
        context.update(
            topic="Python",
            last_assistant_response=(
                "Python is a programming language."
            ),
        )

        request = NaturalConversationBridge().process(
            user_input="Give me one simple example.",
            conversation_context=context,
            conversation_manager=_Conversation(),
        )

        self.assertEqual(request.relation, "follow_up")
        self.assertEqual(request.mode, "conversation")
        self.assertTrue(request.needs_ai)
        self.assertEqual(request.topic, "Python")

    def test_explicit_vision_target_is_not_reclassified_as_chat_follow_up(self):
        context = NaturalContext(
            user_input="Show me another person.",
            conversation={
                "topic": "Python",
                "last_assistant_response": "Here is a Python example.",
            },
        )

        decision = InteractionClassifier().classify(context)

        self.assertNotEqual(decision.intent, "contextual_conversation")

    def test_context_free_another_one_does_not_invent_a_topic(self):
        context = NaturalContext(
            user_input="Show me another one.",
            conversation={},
        )

        decision = InteractionClassifier().classify(context)

        self.assertNotEqual(decision.intent, "contextual_conversation")

    def test_context_free_example_request_is_not_guessed(self):
        context = NaturalContext(
            user_input="Give me an example.",
            conversation={},
        )

        decision = InteractionClassifier().classify(context)

        self.assertNotEqual(decision.mode.value, "conversation")
        self.assertNotEqual(decision.intent, "contextual_conversation")

    def test_action_reference_is_resolved_only_from_active_context(self):
        context = ConversationContextManager()
        context.update(
            application="chrome",
            skill="browser",
            topic="application",
            task="open chrome",
            intent="open",
            action="open",
            object="chrome",
        )

        understanding = ConversationUnderstandingEngine().understand(
            "Close it.",
            state=context,
        )
        follow_up = FollowUpResolver().resolve(
            understanding,
            context,
        )
        plan = FollowUpExecutionBridge().resolve(
            raw_input="Close it.",
            follow_up=follow_up,
        )

        self.assertTrue(follow_up.is_follow_up)
        self.assertEqual(follow_up.resolved_references["it"], "chrome")
        self.assertEqual(plan, [{"action": "close"}])

    def test_unknown_action_reference_is_not_guessed(self):
        context = ConversationContextManager()
        context.update(
            application="google",
            skill="browser",
            topic="search",
            task="search google",
            intent="google_search",
            action="search",
            object="search",
        )

        understanding = ConversationUnderstandingEngine().understand(
            "Close it.",
            state=context,
        )
        follow_up = FollowUpResolver().resolve(
            understanding,
            context,
        )

        self.assertTrue(follow_up.is_follow_up)
        self.assertIsNone(
            FollowUpExecutionBridge().resolve(
                raw_input="Close it.",
                follow_up=follow_up,
            )
        )

    def test_new_speech_session_cancels_old_queued_session(self):
        old_session = create_session()
        new_session = create_session()

        self.assertTrue(is_cancelled(old_session))
        self.assertFalse(is_current(old_session))
        self.assertTrue(is_current(new_session))
        self.assertIs(current_session(), new_session)

        cancel_current()
        self.assertTrue(is_cancelled(new_session))

    def tearDown(self):
        cancel_current()


if __name__ == "__main__":
    unittest.main()
