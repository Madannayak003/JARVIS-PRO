from brain.conversation_context import ConversationContextManager
from brain.reference_resolver import ReferenceResolver


context = ConversationContextManager()
resolver = ReferenceResolver()


# Simulate previous execution
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


print("\n[TEST 1] Resolve 'it'")

result = resolver.resolve(
    "it",
    context,
)

print(result)


print("\n[TEST 2] Resolve 'that'")

result = resolver.resolve(
    "that",
    context,
)

print(result)


print("\n[TEST 3] Resolve 'the music'")

result = resolver.resolve(
    "music",
    context,
)

print(result)