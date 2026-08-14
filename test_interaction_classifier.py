"""
JARVIS PRO
NCI-3 Test

Tests:

    NCI-2 NaturalContext
            ↓
    NCI-3 InteractionClassifier
            ↓
    NCI-1 InteractionDecision
"""

from brain.natural.natural_context import (
    NaturalContext,
)

from brain.natural.interaction_classifier import (
    InteractionClassifier,
)


classifier = (
    InteractionClassifier()
)


def test(
    text,
    conversation=None,
):

    context = NaturalContext(

        user_input=text,

        conversation=(
            conversation or {}
        ),
    )

    decision = (
        classifier.classify(
            context
        )
    )

    print()
    print(
        f"{text}"
    )

    print(
        "  mode       =",
        decision.mode.value,
    )

    print(
        "  intent     =",
        decision.intent,
    )

    print(
        "  confidence =",
        decision.confidence,
    )

    print(
        "  action     =",
        decision.requires_action,
    )

    print(
        "  reason     =",
        decision.reason,
    )

    return decision


# ============================================================
# Conversation
# ============================================================

d1 = test(
    "what is ESP32?"
)

assert d1.is_conversation


d2 = test(
    "tell me about Python"
)

assert d2.is_conversation


d3 = test(
    "how are you"
)

assert d3.is_conversation


# ============================================================
# Explicit actions
# ============================================================

d4 = test(
    "open notepad"
)

assert d4.is_action


d5 = test(
    "play music"
)

assert d5.is_action


d6 = test(
    "search Arduino on Google"
)

assert d6.is_action


d7 = test(
    "play the first video"
)

assert d7.is_action


# ============================================================
# Contextual action
# ============================================================

spotify_context = {

    "application": "spotify",

    "skill": "spotify",

    "topic": "music",

    "task": "play music",

    "object": "music",

}


d8 = test(
    "make it louder",
    spotify_context,
)

assert d8.is_action


d9 = test(
    "pause it",
    spotify_context,
)

assert d9.is_action


d10 = test(
    "resume it",
    spotify_context,
)

assert d10.is_action


# ============================================================
# Contextual conversation
# ============================================================

d11 = test(
    "tell me more about it",
    {
        "application": "spotify",
        "skill": "spotify",
        "topic": "music",
        "task": "play music",
    },
)

assert d11.is_conversation


# ============================================================
# Clarification
# ============================================================

d12 = test(
    "which one?"
)

assert d12.needs_clarification


# ============================================================
# Hybrid
# ============================================================

d13 = test(
    "open VS Code and tell me what we were doing"
)

assert d13.is_hybrid


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print("NCI-3 PASS")
print("=" * 70)