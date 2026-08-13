from brain.conversation_context import ConversationContextManager
from brain.conversation_understanding import (
    ConversationUnderstandingEngine,
)
from brain.reference_resolver import ReferenceResolver
from brain.followup_resolver import FollowUpResolver


# ============================================================
# Create context
# ============================================================

context = ConversationContextManager()


# ============================================================
# Simulate previous executed command
# ============================================================

context.update(
    topic="music",
    task="play music",
    application="spotify",
    skill="spotify",
    intent="spotify_play",
    action="spotify_play",
    object="music",
)


print("\n[CONTEXT]")
print(context.snapshot())


# ============================================================
# Create engines
# ============================================================

understanding_engine = (
    ConversationUnderstandingEngine()
)

reference_resolver = ReferenceResolver()

followup_resolver = FollowUpResolver(
    reference_resolver
)


# ============================================================
# Understand follow-up
# ============================================================

user_input = "make it louder"

understanding = (
    understanding_engine.understand(
        user_input=user_input,
        previous_messages=None,
        state=None,
    )
)


print("\n[UNDERSTANDING]")
print(understanding)


# ============================================================
# Resolve follow-up
# ============================================================

result = followup_resolver.resolve(
    understanding,
    context,
)


print("\n[FOLLOW-UP RESULT]")
print(result)


# ============================================================
# Explicit reference check
# ============================================================

print("\n[REFERENCE CHECK]")

reference = reference_resolver.resolve(
    "it",
    context,
)

print(reference)