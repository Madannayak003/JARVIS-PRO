"""
JARVIS PRO
NCI-9 Test

Verify that the real ContextBuilder produces
AIContext.natural correctly.
"""

from brain.context_builder import ContextBuilder
from brain.conversation_context import (
    ConversationContextManager,
)
from brain.conversation_manager import (
    ConversationManager,
)
from brain.profile_manager import (
    ProfileManager,
)


# ============================================================
# Existing JARVIS managers
# ============================================================

conversation_context = (
    ConversationContextManager()
)

conversation_manager = (
    ConversationManager()
)

profile_manager = (
    ProfileManager()
)


# ============================================================
# Active conversational context
# ============================================================

conversation_context.update(

    application="spotify",

    skill="spotify",

    topic="music",

    task="play music",

    intent="spotify_play",

    action="spotify_play",

    object="music",

)


# ============================================================
# Context Builder
# ============================================================

builder = ContextBuilder(

    profile_manager=(
        profile_manager
    ),

    conversation_manager=(
        conversation_manager
    ),

    conversation_context=(
        conversation_context
    ),

)


# ============================================================
# Build context
# ============================================================

context = builder.build(
    "tell me more about it"
)


# ============================================================
# Display
# ============================================================

print()
print("=" * 70)
print("NCI-9 CONTEXT BUILDER")
print("=" * 70)

print()
print("AIContext.natural:")
print()

for key, value in context.natural.items():

    print(
        f"{key:<20} = {value}"
    )


# ============================================================
# Assertions
# ============================================================

assert context.natural

assert (
    context.natural["intent"]
    == "explain_current_subject"
)

assert (
    context.natural["mode"]
    == "conversation"
)

assert (
    context.natural["reference"]
    == "it"
)

assert (
    context.natural["application"]
    == "spotify"
)

assert (
    context.natural["skill"]
    == "spotify"
)

assert (
    context.natural["needs_ai"]
    is True
)

assert (
    context.natural["needs_action"]
    is False
)


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print("NCI-9 PASS")
print("=" * 70)