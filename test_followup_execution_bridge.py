from brain.followup_execution_bridge import (
    FollowUpExecutionBridge,
)

from brain.followup_resolver import (
    FollowUpResolution,
)


bridge = FollowUpExecutionBridge()


def test(
    text,
    application,
    skill,
):

    follow_up = FollowUpResolution(

        is_follow_up=True,

        raw_input=text,

        relation="follow_up",

        application=application,

        skill=skill,

        topic="test",

        task="test",

        intent="test",

        action="test",

        object="test",

        references=["it"],

        resolved_references={
            "it": "test"
        },

        unresolved_references=[],

        confidence=0.9,

        reason="test",

    )

    result = bridge.resolve(

        raw_input=text,

        follow_up=follow_up,

    )

    print(
        f"{application:10} | "
        f"{text:25} -> "
        f"{result}"
    )


print("\n=== SPOTIFY ===")

test(
    "make it louder",
    "spotify",
    "spotify",
)

test(
    "pause it",
    "spotify",
    "spotify",
)

test(
    "resume it",
    "spotify",
    "spotify",
)

test(
    "next",
    "spotify",
    "spotify",
)

test(
    "previous",
    "spotify",
    "spotify",
)


print("\n=== YOUTUBE ===")

test(
    "pause it",
    "youtube",
    "youtube",
)

test(
    "resume it",
    "youtube",
    "youtube",
)

test(
    "next",
    "youtube",
    "youtube",
)

test(
    "previous",
    "youtube",
    "youtube",
)


print("\n=== SYSTEM ===")

test(
    "make it louder",
    "system",
    "system",
)

test(
    "make it quieter",
    "system",
    "system",
)

print("\n=== WINDOWS ===")

for app in ["notepad", "calculator"]:

    follow_up = FollowUpResolution(
        is_follow_up=True,
        raw_input="close it",
        relation="follow_up",
        application=app,
        skill="system",
        topic="application",
        task=f"open {app}",
        intent="open",
        action="open",
        object=app,
        references=["it"],
        resolved_references={"it": app},
        unresolved_references=[],
        confidence=0.88,
        reason="test",
    )

    result = bridge.resolve(
        raw_input="close it",
        follow_up=follow_up,
    )

    print(
        app,
        "->",
        result,
    )


print("\n=== SYSTEM ===")

follow_up = FollowUpResolution(
    is_follow_up=True,
    raw_input="make it quieter",
    relation="follow_up",
    application="system",
    skill="system",
    topic="system",
    task="increase volume",
    intent="volume",
    action="increase_volume",
    object="system volume",
    references=["it"],
    resolved_references={
        "it": "system volume"
    },
    unresolved_references=[],
    confidence=0.88,
    reason="test",
)

result = bridge.resolve(
    raw_input="make it quieter",
    follow_up=follow_up,
)

print(
    "make it quieter ->",
    result,
)