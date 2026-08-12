from brain.conversation_context import (
    ConversationContextManager
)


context = ConversationContextManager()


print("\n[TEST 1] Empty context")
print(context.snapshot())


print("\n[TEST 2] Spotify context")

context.update(
    topic="music",
    task="play music",
    application="spotify",
    skill="spotify",
    intent="spotify_play",
    action="play",
    object="music",
)

context.set_user_input(
    "play some music"
)

context.set_relation(
    "new_request"
)

print(context.snapshot())


print("\n[TEST 3] Follow-up")

context.set_user_input(
    "make it louder"
)

context.set_relation(
    "follow_up"
)

context.set_referenced_object(
    "music"
)

context.set_action(
    "increase_volume"
)

print(context.snapshot())


print("\n[TEST 4] Pending clarification")

context.set_pending_question(
    "Which platform should I search?"
)

context.set_pending_clarification(
    "search_platform"
)

print(context.snapshot())


print("\n[TEST 5] Clear pending")

context.clear_pending()

print(context.snapshot())


print("\n[TEST 6] Clear task")

context.clear_task()

print(context.snapshot())