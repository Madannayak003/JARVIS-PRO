"""
JARVIS PRO
NCI-6 Test
"""

from brain.natural.conversation_request import (
    ConversationRequestBuilder,
)

from brain.natural.response_strategy import (
    ResponseStrategyEngine,
)

from brain.natural.meaning_understanding import (
    MeaningUnderstandingEngine,
)

from brain.natural.interaction_classifier import (
    InteractionClassifier,
)

from brain.natural.natural_context import (
    NaturalContext,
)


classifier = InteractionClassifier()

meaning_engine = (
    MeaningUnderstandingEngine()
)

strategy_engine = (
    ResponseStrategyEngine()
)

request_builder = (
    ConversationRequestBuilder()
)


def run_test(
    command,
    conversation=None
):

    context = NaturalContext(

        user_input=command,

        conversation=(
            conversation or {}
        ),

        profile={
            "name": "Madan",
            "current_project": "JARVIS PRO",
        },

        project={
            "name": "JARVIS PRO"
        },
    )

    # ========================================================
    # NCI-3
    # ========================================================

    decision = classifier.classify(
        context
    )

    # ========================================================
    # NCI-4
    # ========================================================

    meaning = meaning_engine.understand(
        context=context,
        decision=decision,
    )

    # ========================================================
    # NCI-5
    # ========================================================

    strategy = strategy_engine.decide(
        meaning
    )

    # ========================================================
    # NCI-6
    # ========================================================

    request = request_builder.build(

        user_input=command,

        meaning=meaning,

        strategy=strategy,

        context=context
    )

    print()
    print("=" * 70)
    print(command)
    print("=" * 70)

    print(
        "intent          =",
        request.intent
    )

    print(
        "mode            =",
        request.mode
    )

    print(
        "topic           =",
        request.topic
    )

    print(
        "task            =",
        request.task
    )

    print(
        "object          =",
        request.object
    )

    print(
        "reference       =",
        request.reference
    )

    print(
        "application     =",
        request.application
    )

    print(
        "skill           =",
        request.skill
    )

    print(
        "needs_ai        =",
        request.needs_ai
    )

    print(
        "needs_action    =",
        request.needs_action
    )

    print(
        "needs_clarify   =",
        request.needs_clarification
    )

    print(
        "instructions    =",
        request.instructions
    )

    return request


# ============================================================
# TEST 1
# Natural conversation
# ============================================================

r1 = run_test(
    "what do you think about our project"
)

assert r1.mode == "conversation"
assert r1.needs_ai is True
assert r1.needs_action is False
assert r1.intent == "project_discussion"


# ============================================================
# TEST 2
# Contextual conversation
# ============================================================

r2 = run_test(

    "tell me more about it",

    conversation={

        "application": "spotify",

        "skill": "spotify",

        "topic": "music",

        "task": "play music",

        "object": "music",
    }
)

assert r2.mode == "conversation"
assert r2.needs_ai is True
assert r2.needs_action is False
assert r2.application == "spotify"
assert r2.skill == "spotify"


# ============================================================
# TEST 3
# Action
# ============================================================

r3 = run_test(
    "open notepad"
)

assert r3.mode == "action"
assert r3.needs_action is True
assert r3.needs_ai is False


# ============================================================
# TEST 4
# Contextual action
# ============================================================

r4 = run_test(

    "make it louder",

    conversation={

        "application": "spotify",

        "skill": "spotify",

        "topic": "music",

        "task": "play music",

        "object": "music",
    }
)

assert r4.mode == "action"
assert r4.needs_action is True
assert r4.needs_ai is False


# ============================================================
# TEST 5
# Clarification
# ============================================================

r5 = run_test(
    "which one?"
)

assert r5.mode == "clarification"
assert r5.needs_clarification is True
assert r5.needs_action is False


# ============================================================
# TEST 6
# Hybrid
# ============================================================

r6 = run_test(
    "open VS Code and tell me what we were doing"
)

assert r6.mode == "hybrid"
assert r6.needs_action is True
assert r6.needs_ai is True


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print("NCI-6 PASS")
print("=" * 70)