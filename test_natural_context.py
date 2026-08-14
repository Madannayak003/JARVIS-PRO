"""
JARVIS PRO
NCI-2 Test

Tests NaturalContextAggregator independently.

This test does NOT:
    - start JARVIS
    - call dispatcher
    - call fast router
    - execute skills
    - call planner
    - call an AI model
"""

from brain.natural.natural_context import (
    NaturalContextAggregator,
)


# ============================================================
# Fake Conversation Context
# ============================================================

class FakeConversationContext:

    def snapshot(self):

        return {
            "topic": "music",
            "task": "play music",
            "application": "spotify",
            "skill": "spotify",
            "intent": "spotify_play",
            "action": "spotify_play",
            "object": "music",
            "last_result": True,
        }


# ============================================================
# Fake Conversation Manager
# ============================================================

class FakeMessage:

    def __init__(
        self,
        role,
        content,
    ):

        self.role = role
        self.content = content


class FakeConversationManager:

    def get_recent_messages(
        self,
        limit=10,
    ):

        return [

            FakeMessage(
                "user",
                "play music",
            ),

            FakeMessage(
                "assistant",
                "Playing music.",
            ),

        ][:limit]


# ============================================================
# Fake Profile Manager
# ============================================================

class FakeProfileManager:

    def as_dict(self):

        return {

            "name": "Madan",

            "preferred_language": (
                "English"
            ),

            "coding_language": (
                "Python"
            ),

            "ide": (
                "VS Code"
            ),

            "current_project": (
                "JARVIS PRO"
            ),

        }


# ============================================================
# Fake Conversation State
# ============================================================

class FakeStateManager:

    def info(self):

        return {

            "owner": "spotify",

            "reason": (
                "music playback"
            ),

        }


# ============================================================
# Fake AI Context
# ============================================================

class FakeAIContext:

    user_input = (
        "make it louder"
    )

    memories = [

        "User prefers Python.",

    ]

    planner = {

        "active": False,

    }

    project = {

        "name": (
            "JARVIS PRO"
        ),

    }

    screen = {}


# ============================================================
# Build
# ============================================================

aggregator = (
    NaturalContextAggregator()
)


context = aggregator.build(

    user_input=(
        "make it louder"
    ),

    conversation_context=(
        FakeConversationContext()
    ),

    conversation_manager=(
        FakeConversationManager()
    ),

    profile_manager=(
        FakeProfileManager()
    ),

    state_manager=(
        FakeStateManager()
    ),

    ai_context=(
        FakeAIContext()
    ),

)


# ============================================================
# Display
# ============================================================

print()
print("=" * 70)
print("NCI-2 NATURAL CONTEXT")
print("=" * 70)

print()

print(
    "User input:",
    context.user_input,
)

print(
    "Application:",
    context.conversation.get(
        "application"
    ),
)

print(
    "Skill:",
    context.conversation.get(
        "skill"
    ),
)

print(
    "Topic:",
    context.conversation.get(
        "topic"
    ),
)

print(
    "Task:",
    context.conversation.get(
        "task"
    ),
)

print(
    "Object:",
    context.conversation.get(
        "object"
    ),
)

print(
    "Recent messages:",
    len(
        context.recent_messages
    ),
)

print(
    "Profile:",
    context.profile,
)

print(
    "Memories:",
    context.memories,
)

print(
    "Planner:",
    context.planner,
)

print(
    "Project:",
    context.project,
)

print(
    "Screen:",
    context.screen,
)

print(
    "Conversation state:",
    context.conversation_state,
)

print(
    "Metadata:",
    context.metadata,
)


# ============================================================
# Assertions
# ============================================================

assert (
    context.user_input
    == "make it louder"
)

assert (
    context.conversation[
        "application"
    ]
    == "spotify"
)

assert (
    context.conversation[
        "skill"
    ]
    == "spotify"
)

assert (
    context.conversation[
        "topic"
    ]
    == "music"
)

assert (
    context.conversation[
        "task"
    ]
    == "play music"
)

assert (
    context.conversation[
        "object"
    ]
    == "music"
)

assert (
    len(
        context.recent_messages
    )
    == 2
)

assert (
    context.profile[
        "name"
    ]
    == "Madan"
)

assert (
    len(
        context.memories
    )
    == 1
)

assert (
    context.project[
        "name"
    ]
    == "JARVIS PRO"
)

assert (
    context.conversation_state[
        "owner"
    ]
    == "spotify"
)


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print("NCI-2 PASS")
print("=" * 70)