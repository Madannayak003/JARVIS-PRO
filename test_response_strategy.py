"""
JARVIS PRO
NCI-5 Test
"""

from brain.natural.natural_context import (
    NaturalContext,
)

from brain.natural.interaction_classifier import (
    InteractionClassifier,
)

from brain.natural.meaning_understanding import (
    MeaningUnderstandingEngine,
)

from brain.natural.response_strategy import (
    ResponseStrategyEngine,
)


classifier = InteractionClassifier()

meaning_engine = (
    MeaningUnderstandingEngine()
)

strategy_engine = (
    ResponseStrategyEngine()
)


def test(command, conversation=None):

    context = NaturalContext(

        user_input=command,

        conversation=(
            conversation or {}
        ),

        profile={
            "current_project": "JARVIS PRO"
        },

        project={
            "name": "JARVIS PRO"
        },
    )

    decision = classifier.classify(
        context
    )

    meaning = meaning_engine.understand(
        context=context,
        decision=decision,
    )

    strategy = strategy_engine.decide(
        meaning
    )

    print()
    print("=" * 70)
    print(command)
    print("=" * 70)

    print(
        "meaning     =",
        meaning.intent,
    )

    print(
        "mode        =",
        strategy.mode.value,
    )

    print(
        "needs_action =",
        strategy.needs_action,
    )

    print(
        "needs_ai    =",
        strategy.needs_ai,
    )

    print(
        "needs_clarification =",
        strategy.needs_clarification,
    )

    print(
        "confidence  =",
        strategy.confidence,
    )

    print(
        "reason      =",
        strategy.reason,
    )

    return strategy


# ============================================================
# 1. Natural conversation
# ============================================================

d1 = test(
    "what do you think about our project"
)

assert (
    d1.mode.value
    == "conversation"
)

assert (
    d1.needs_action
    is False
)

assert (
    d1.needs_ai
    is True
)


# ============================================================
# 2. Normal action
# ============================================================

d2 = test(
    "open notepad"
)

assert (
    d2.mode.value
    == "action"
)

assert (
    d2.needs_action
    is True
)

assert (
    d2.needs_ai
    is False
)


# ============================================================
# 3. Contextual action
# ============================================================

d3 = test(
    "make it louder",
    conversation={
        "application": "spotify",
        "skill": "spotify",
        "topic": "music",
        "task": "play music",
        "object": "music",
    },
)

assert (
    d3.mode.value
    == "action"
)

assert (
    d3.needs_action
    is True
)

assert (
    d3.needs_ai
    is False
)


# ============================================================
# 4. Contextual conversation
# ============================================================

d4 = test(
    "tell me more about it",
    conversation={
        "application": "spotify",
        "skill": "spotify",
        "topic": "music",
        "task": "play music",
        "object": "music",
    },
)

assert (
    d4.mode.value
    == "conversation"
)

assert (
    d4.needs_action
    is False
)

assert (
    d4.needs_ai
    is True
)


# ============================================================
# 5. Clarification
# ============================================================

d5 = test(
    "which one?"
)

assert (
    d5.mode.value
    == "clarification"
)

assert (
    d5.needs_clarification
    is True
)


# ============================================================
# 6. Hybrid
# ============================================================

d6 = test(
    "open VS Code and tell me what we were doing"
)

assert (
    d6.mode.value
    == "hybrid"
)

assert (
    d6.needs_action
    is True
)

assert (
    d6.needs_ai
    is True
)


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print("NCI-5 PASS")
print("=" * 70)