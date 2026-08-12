from brain.conversation_context import (
    ConversationContextManager
)

from brain.conversation_coordinator import (
    ConversationCoordinator
)


# ============================================================
# Create coordinator
# ============================================================

context = ConversationContextManager()

coordinator = ConversationCoordinator(
    context_manager=context
)


# ============================================================
# Seed context
# ============================================================

coordinator.record_execution(

    topic="music",

    task="play music",

    application="spotify",

    skill="spotify",

    intent="spotify_play",

    action="play",

    object="music",

)


# ============================================================
# TEST 1
# ============================================================

print(
    "\n[TEST 1] "
    "Make it louder"
)

result = coordinator.observe(
    "make it louder"
)

print(
    "Relation:",
    result.understanding.relation
)

print(
    "References:",
    result.understanding.references
)

print(
    "Resolved:",
    result.follow_up.resolved_references
)

print(
    "Application:",
    result.follow_up.application
)

print(
    "Object:",
    result.follow_up.object
)


# ============================================================
# TEST 2
# ============================================================

print(
    "\n[TEST 2] "
    "Open Chrome"
)

result = coordinator.observe(
    "open chrome"
)

print(
    "Relation:",
    result.understanding.relation
)

print(
    "Follow-up:",
    result.follow_up.is_follow_up
)

print(
    "Context:",
    result.context
)


# ============================================================
# TEST 3
# ============================================================

print(
    "\n[TEST 3] "
    "Clarification"
)

coordinator.start_clarification(

    field="search_platform",

    question="Which platform should I search?",

    task="search Python tutorials",

    owner="browser",

)

result = coordinator.observe(
    "google"
)

print(
    "Waiting:",
    result.clarification_waiting
)

print(
    "Field:",
    result.clarification_field
)

print(
    "Question:",
    result.clarification_question
)


# ============================================================
# TEST 4
# ============================================================

print(
    "\n[TEST 4] "
    "Resolve clarification"
)

resolved = (
    coordinator.resolve_clarification(
        "google"
    )
)

print(
    "Resolved:",
    resolved
)

print(
    "Info:",
    coordinator.info()
)