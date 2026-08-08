from brain.intent_engine import IntentEngine


engine = IntentEngine()


tests = [

    (
        "create a python calculator",
        "developer",
    ),

    (
        "build an html website",
        "developer",
    ),

    (
        "add subtract function",
        "developer",
    ),

    (
        "fix the divide function",
        "developer",
    ),

    (
        "write python code",
        "developer",
    ),

    (
        "what is python",
        "chat",
    ),

    (
        "explain python",
        "chat",
    ),

    (
        "tell me a joke",
        "chat",
    ),

    (
        "open chrome",
        "planner",
    ),

]


for command, expected in tests:

    result = engine.detect(
        command
    )

    print(
        f"{command:<35}"
        f" → {result.mode:<10}"
        f" expected={expected}"
    )

    assert (
        result.mode
        == expected
    )


print()
print(
    "INTENT ENGINE TEST PASSED"
)