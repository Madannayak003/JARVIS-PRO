from brain.conversation_understanding import (
    understand,
    ConversationRelation,
)


tests = [
    "open spotify",
    "play music",
    "make it louder",
    "actually use youtube",
    "yes",
    "no",
    "never mind",
    "continue",
    "the first one",
    "tell me a joke",
]


for text in tests:

    result = understand(text)

    print(
        f"{text!r:25} -> "
        f"{result.relation.value:22} "
        f"confidence={result.confidence}"
    )