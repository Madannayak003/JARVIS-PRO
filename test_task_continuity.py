from brain.conversation_understanding import (
    ConversationUnderstandingEngine,
)

from brain.followup_resolver import (
    FollowUpResolver,
)

from brain.conversation_context import (
    ConversationContextManager,
)


context = ConversationContextManager()

resolver = FollowUpResolver()

understanding_engine = (
    ConversationUnderstandingEngine()
)


def test(command):

    print()
    print("=" * 70)
    print(command)
    print("=" * 70)

    understanding = (
        understanding_engine.understand(
            user_input=command,
            previous_messages=None,
            state=None,
        )
    )

    print()
    print("[UNDERSTANDING]")
    print(understanding)

    result = resolver.resolve(
        understanding,
        context,
    )

    print()
    print("[FOLLOW-UP]")
    print(result)

    return result


# ============================================================
# Initial YouTube task
# ============================================================

context.update(
    application="youtube",
    skill="youtube",
    topic="video",
    task="search youtube",
    intent="youtube_search",
    action="search",
    object="ESP32",
)


print()
print("=" * 70)
print("ACTIVE CONTEXT")
print("=" * 70)

print(
    context.snapshot()
)


# ============================================================
# TEST 1
# ============================================================

test(
    "play the first video"
)


# ============================================================
# TEST 2
# ============================================================

test(
    "pause it"
)


# ============================================================
# TEST 3
# ============================================================

test(
    "resume it"
)


# ============================================================
# TEST 4
# ============================================================

test(
    "search Arduino on Google"
)