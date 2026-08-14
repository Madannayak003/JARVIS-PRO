"""
JARVIS PRO
NCI-8 Test

Tests NCI using the real JARVIS context managers.
"""

from brain.natural.natural_bridge import (
    NaturalConversationBridge,
)

from brain.conversation_context import (
    ConversationContextManager,
)

from brain.conversation_manager import (
    ConversationManager,
)

from brain.profile_manager import (
    ProfileManager,
)

from brain.context_types import (
    AIContext,
)


# ============================================================
# Existing JARVIS objects
# ============================================================

conversation_context = (
    ConversationContextManager()
)

conversation_manager = (
    ConversationManager()
)

profile_manager = ProfileManager()

ai_context = AIContext()


# ============================================================
# Prepare active context
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
# Bridge
# ============================================================

bridge = (
    NaturalConversationBridge()
)


# ============================================================
# Test
# ============================================================

result = bridge.process(

    user_input="tell me more about it",

    conversation_context=(
        conversation_context
    ),

    conversation_manager=(
        conversation_manager
    ),

    profile_manager=(
        profile_manager
    ),

    state_manager=None,

    ai_context=(
        ai_context
    ),
)


print()
print("=" * 70)
print("NCI-8 REAL CONTEXT")
print("=" * 70)

print(
    "intent       =",
    result.intent
)

print(
    "mode         =",
    result.mode
)

print(
    "topic        =",
    result.topic
)

print(
    "task         =",
    result.task
)

print(
    "object       =",
    result.object
)

print(
    "reference    =",
    result.reference
)

print(
    "application  =",
    result.application
)

print(
    "skill        =",
    result.skill
)

print(
    "needs_ai     =",
    result.needs_ai
)

print(
    "needs_action =",
    result.needs_action
)

print(
    "confidence   =",
    result.confidence
)


# ============================================================
# Assertions
# ============================================================

assert result.intent == (
    "explain_current_subject"
)

assert result.mode == (
    "conversation"
)

assert result.reference == "it"

assert result.application == (
    "spotify"
)

assert result.skill == (
    "spotify"
)

assert result.needs_ai is True

assert result.needs_action is False


print()
print("=" * 70)
print("NCI-8 PASS")
print("=" * 70)