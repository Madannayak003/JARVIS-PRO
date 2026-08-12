from brain.conversation_context import (
    ConversationContextManager
)

from brain.reference_resolver import (
    ReferenceResolver
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


resolver = ReferenceResolver()


# ============================================================
# TEST 1
# ============================================================

print("\n[TEST 1] Resolve 'it'")

result = resolver.resolve(
    "it",
    context
)

print(result)


# ============================================================
# TEST 2
# ============================================================

print("\n[TEST 2] Resolve 'that'")

result = resolver.resolve(
    "that",
    context
)

print(result)


# ============================================================
# TEST 3
# ============================================================

print("\n[TEST 3] Resolve 'same'")

result = resolver.resolve(
    "same",
    context
)

print(result)


# ============================================================
# TEST 4
# ============================================================

print("\n[TEST 4] Resolve first item")

context.update(
    objects=[
        "Python tutorial",
        "JavaScript tutorial",
        "React tutorial",
    ]
)

result = resolver.resolve(
    "the first one",
    context
)

print(result)


# ============================================================
# TEST 5
# ============================================================

print("\n[TEST 5] Resolve second item")

result = resolver.resolve(
    "the second one",
    context
)

print(result)


# ============================================================
# TEST 6
# ============================================================

print("\n[TEST 6] Resolve last item")

result = resolver.resolve(
    "the last one",
    context
)

print(result)


# ============================================================
# TEST 7
# ============================================================

print("\n[TEST 7] Unknown reference")

empty_context = ConversationContextManager()

result = resolver.resolve(
    "it",
    empty_context
)

print(result)