from brain.followup_resolver import FollowUpResolver
from brain.conversation_understanding import (
    ConversationUnderstanding,
    ConversationRelation,
)
from brain.conversation_context import (
    ConversationContextManager,
)


# ============================================================
# Helpers
# ============================================================

def test_followup(
    *,
    name,
    application,
    skill,
    topic,
    task,
    intent,
    action,
    object,
    command,
    references,
):

    context = ConversationContextManager()

    context.update(
        application=application,
        skill=skill,
        topic=topic,
        task=task,
        intent=intent,
        action=action,
        object=object,
    )

    resolver = FollowUpResolver()

    understanding = ConversationUnderstanding(
        relation=ConversationRelation.FOLLOW_UP,
        confidence=0.8,
        reason="test follow-up",
        raw_input=command,
        references=references,
    )

    result = resolver.resolve(
        understanding,
        context,
    )

    print()
    print("=" * 70)
    print(name)
    print("=" * 70)
    print("Command:")
    print(command)
    print()
    print("Result:")
    print(result)


# ============================================================
# TEST 1
# Notepad
# ============================================================

test_followup(
    name="NOTEPAD → CLOSE IT",

    application="notepad",
    skill="system",
    topic="application",
    task="open notepad",
    intent="open",
    action="open",
    object="notepad",

    command="close it",
    references=["it"],
)


# ============================================================
# TEST 2
# Calculator
# ============================================================

test_followup(
    name="CALCULATOR → CLOSE IT",

    application="calculator",
    skill="system",
    topic="application",
    task="open calculator",
    intent="open",
    action="open",
    object="calculator",

    command="close it",
    references=["it"],
)


# ============================================================
# TEST 3
# System volume
# ============================================================

test_followup(
    name="SYSTEM VOLUME → MAKE IT QUIETER",

    application="system",
    skill="system",
    topic="system",
    task="increase volume",
    intent="volume",
    action="increase_volume",
    object="system volume",

    command="make it quieter",
    references=["it"],
)