from brain.conversation_context import (
    ConversationContextManager
)

from brain.conversation_understanding import (
    ConversationUnderstandingEngine
)

from brain.followup_resolver import (
    FollowUpResolver
)


# ============================================================
# Create context
# ============================================================

context = ConversationContextManager()

context.update(

    topic="music",

    task="play music",

    application="spotify",

    skill="spotify",

    intent="spotify_play",

    action="play",

    object="music",

)


# ============================================================
# Create engines
# ============================================================

understanding_engine = (
    ConversationUnderstandingEngine()
)

followup_resolver = FollowUpResolver()


# ============================================================
# TEST 1
# ============================================================

print(
    "\n[TEST 1] "
    "Make it louder"
)

understanding = (
    understanding_engine.understand(
        "make it louder"
    )
)

result = (
    followup_resolver.resolve(
        understanding,
        context
    )
)

print(
    "Understanding:",
    understanding
)

print(
    "Follow-up:",
    result
)


# ============================================================
# TEST 2
# ============================================================

print(
    "\n[TEST 2] "
    "Change that"
)

understanding = (
    understanding_engine.understand(
        "change that"
    )
)

result = (
    followup_resolver.resolve(
        understanding,
        context
    )
)

print(
    "Understanding:",
    understanding
)

print(
    "Follow-up:",
    result
)


# ============================================================
# TEST 3
# ============================================================

print(
    "\n[TEST 3] "
    "The first one"
)

context.update(
    objects=[
        "Python tutorial",
        "JavaScript tutorial",
        "React tutorial",
    ]
)

understanding = (
    understanding_engine.understand(
        "the first one"
    )
)

result = (
    followup_resolver.resolve(
        understanding,
        context
    )
)

print(
    "Understanding:",
    understanding
)

print(
    "Follow-up:",
    result
)


# ============================================================
# TEST 4
# ============================================================

print(
    "\n[TEST 4] "
    "Continue"
)

understanding = (
    understanding_engine.understand(
        "continue"
    )
)

result = (
    followup_resolver.resolve(
        understanding,
        context
    )
)

print(
    "Understanding:",
    understanding
)

print(
    "Follow-up:",
    result
)


# ============================================================
# TEST 5
# ============================================================

print(
    "\n[TEST 5] "
    "Open Chrome"
)

understanding = (
    understanding_engine.understand(
        "open chrome"
    )
)

result = (
    followup_resolver.resolve(
        understanding,
        context
    )
)

print(
    "Understanding:",
    understanding
)

print(
    "Follow-up:",
    result
)