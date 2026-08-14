"""
JARVIS PRO
NCI-10 - Natural Prompt Integration Test
"""

from brain.context_types import AIContext
from brain.prompt_builder import PromptBuilder


# ============================================================
# Create context
# ============================================================

context = AIContext()

context.user_input = (
    "tell me more about it"
)

context.profile = {
    "name": "Madan",
    "preferred_language": "English",
    "coding_language": "Python",
    "ide": "VS Code",
    "current_project": "JARVIS PRO",
    "response_style": "Detailed",
}

context.project = {
    "name": "JARVIS PRO"
}

context.natural = {

    "user_input":
        "tell me more about it",

    "intent":
        "explain_current_subject",

    "mode":
        "conversation",

    "confidence":
        0.93,

    "topic":
        "music",

    "task":
        "play music",

    "object":
        "music",

    "reference":
        "it",

    "application":
        "spotify",

    "skill":
        "spotify",

    "needs_ai":
        True,

    "needs_action":
        False,

    "needs_clarification":
        False,

    "instructions":
        (
            "Respond naturally as part of "
            "the ongoing conversation. "
            "The user referenced: it."
        ),

    "metadata":
        {
            "nci_stage": "NCI-6"
        }
}


# ============================================================
# Build prompt
# ============================================================

builder = PromptBuilder()

prompt = builder.build(
    context
)


# ============================================================
# Display
# ============================================================

print()
print("=" * 70)
print("NCI-10 NATURAL PROMPT")
print("=" * 70)

print()
print(prompt)


# ============================================================
# Assertions
# ============================================================

assert (
    "NATURAL CONVERSATION INTELLIGENCE"
    in prompt
)

assert (
    "explain_current_subject"
    in prompt
)

assert (
    "conversation"
    in prompt
)

assert (
    "music"
    in prompt
)

assert (
    "play music"
    in prompt
)

assert (
    "spotify"
    in prompt
)

assert (
    "tell me more about it"
    in prompt
)

assert (
    "Needs AI: True"
    in prompt
)

assert (
    "Needs Action: False"
    in prompt
)


# ============================================================
# PASS
# ============================================================

print()
print("=" * 70)
print("NCI-10 PASS")
print("=" * 70)