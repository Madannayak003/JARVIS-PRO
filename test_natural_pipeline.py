"""
JARVIS PRO
NCI-7 Test
"""

from brain.natural.natural_pipeline import (
    NaturalConversationPipeline,
)

from brain.natural.natural_context import (
    NaturalContext,
)


pipeline = (
    NaturalConversationPipeline()
)


def test(
    command,
    conversation=None,
    profile=None,
    project=None,
):

    context = NaturalContext(

        user_input=command,

        conversation=(
            conversation or {}
        ),

        profile=(
            profile
            or {
                "name": "Madan",
                "preferred_language": "English",
                "coding_language": "Python",
                "ide": "VS Code",
                "current_project": "JARVIS PRO",
            }
        ),

        project=(
            project
            or {
                "name": "JARVIS PRO"
            }
        ),
    )

    result = pipeline.process(
        context=context
    )

    print()
    print("=" * 70)
    print(command)
    print("=" * 70)

    print(
        "intent          =",
        result.intent
    )

    print(
        "mode            =",
        result.mode
    )

    print(
        "confidence      =",
        result.confidence
    )

    print(
        "topic           =",
        result.topic
    )

    print(
        "task            =",
        result.task
    )

    print(
        "object          =",
        result.object
    )

    print(
        "reference       =",
        result.reference
    )

    print(
        "application     =",
        result.application
    )

    print(
        "skill           =",
        result.skill
    )

    print(
        "needs_ai        =",
        result.needs_ai
    )

    print(
        "needs_action    =",
        result.needs_action
    )

    print(
        "needs_clarify   =",
        result.needs_clarification
    )

    return result


# ============================================================
# TEST 1
# ============================================================

r1 = test(
    "what do you think about our project"
)

assert r1.mode == "conversation"
assert r1.intent == "project_discussion"
assert r1.needs_ai is True
assert r1.needs_action is False


# ============================================================
# TEST 2
# ============================================================

r2 = test(

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
assert r2.intent == "explain_current_subject"
assert r2.application == "spotify"
assert r2.skill == "spotify"
assert r2.reference == "it"
assert r2.needs_ai is True


# ============================================================
# TEST 3
# ============================================================

r3 = test(
    "open notepad"
)

assert r3.mode == "action"
assert r3.needs_action is True
assert r3.needs_ai is False


# ============================================================
# TEST 4
# ============================================================

r4 = test(

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
# ============================================================

r5 = test(
    "which one?"
)

assert r5.mode == "clarification"
assert r5.intent == "clarification"
assert r5.needs_clarification is True


# ============================================================
# TEST 6
# ============================================================

r6 = test(
    "open VS Code and tell me what we were doing"
)

assert r6.mode == "hybrid"
assert r6.intent == "hybrid_request"
assert r6.needs_action is True
assert r6.needs_ai is True


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print("NCI-7 PASS")
print("=" * 70)