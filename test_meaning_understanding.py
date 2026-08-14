"""
JARVIS PRO
NCI-4 Test

Tests:

    NCI-2 Context
          ↓
    NCI-3 Classification
          ↓
    NCI-4 Meaning
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


classifier = (
    InteractionClassifier()
)

engine = (
    MeaningUnderstandingEngine()
)


# ============================================================
# Helper
# ============================================================

def test(
    command,
    *,
    conversation=None,
    project=None,
):

    context = NaturalContext(

        user_input=command,

        conversation=(
            conversation or {}
        ),

        project=(
            project or {}
        ),

        profile={
            "current_project": (
                "JARVIS PRO"
            )
        },
    )

    decision = (
        classifier.classify(
            context
        )
    )

    meaning = (
        engine.understand(
            context=context,
            decision=decision,
        )
    )

    print()
    print("=" * 70)
    print(command)
    print("=" * 70)

    print(
        "mode        =",
        meaning.mode.value,
    )

    print(
        "intent      =",
        meaning.intent,
    )

    print(
        "topic       =",
        meaning.topic,
    )

    print(
        "task        =",
        meaning.task,
    )

    print(
        "object      =",
        meaning.object,
    )

    print(
        "reference   =",
        meaning.reference,
    )

    print(
        "application =",
        meaning.application,
    )

    print(
        "skill       =",
        meaning.skill,
    )

    print(
        "confidence  =",
        meaning.confidence,
    )

    print(
        "reason      =",
        meaning.reason,
    )

    return meaning


# ============================================================
# 1. Project discussion
# ============================================================

d1 = test(
    "what do you think about our project",
    project={
        "name": "JARVIS PRO"
    },
)

assert (
    d1.intent
    == "project_discussion"
)

assert (
    d1.object
    == "JARVIS PRO"
)


# ============================================================
# 2. Continue previous work
# ============================================================

d2 = test(
    "what were we doing",
    conversation={
        "topic": "developer mode",
        "task": "build generator engine",
        "application": None,
        "skill": None,
        "object": "generator",
    },
)

assert (
    d2.intent
    == "continue_context"
)

assert (
    d2.topic
    == "developer mode"
)


# ============================================================
# 3. Explain current subject
# ============================================================

d3 = test(
    "tell me more about it",
    conversation={
        "topic": "music",
        "task": "play music",
        "application": "spotify",
        "skill": "spotify",
        "object": "music",
    },
)

assert (
    d3.intent
    == "explain_current_subject"
)

assert (
    d3.reference
    == "it"
)

assert (
    d3.object
    == "music"
)


# ============================================================
# 4. Contextual question
# ============================================================

d4 = test(
    "what is it",
    conversation={
        "topic": "ESP32",
        "task": "build weather station",
        "application": None,
        "skill": None,
        "object": "ESP32",
    },
)

assert (
    d4.intent
    == "contextual_question"
)

assert (
    d4.topic
    == "ESP32"
)


# ============================================================
# 5. Current media question
# ============================================================

d5 = test(
    "what am i listening to",
    conversation={
        "topic": "music",
        "task": "play music",
        "application": "spotify",
        "skill": "spotify",
        "object": "music",
    },
)

assert (
    d5.intent
    == "current_media_question"
)

assert (
    d5.application
    == "spotify"
)


# ============================================================
# 6. General conversation
# ============================================================

d6 = test(
    "tell me something interesting"
)

assert (
    d6.intent
    == "general_conversation"
)


# ============================================================
# 7. Action meaning preserved
# ============================================================

d7 = test(
    "open notepad"
)

assert (
    d7.intent
    == "action"
)


# ============================================================
# 8. Hybrid
# ============================================================

d8 = test(
    "open VS Code and tell me what we were doing"
)

assert (
    d8.intent
    == "hybrid_request"
)


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print("NCI-4 PASS")
print("=" * 70)