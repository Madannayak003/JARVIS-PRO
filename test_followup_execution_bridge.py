from brain.followup_execution_bridge import (
    FollowUpExecutionBridge,
)

from brain.followup_resolver import (
    FollowUpResolution,
)


bridge = FollowUpExecutionBridge()


follow_up = FollowUpResolution(
    is_follow_up=True,
    raw_input="make it louder",
    relation="follow_up",
    application="spotify",
    skill="spotify",
    topic="music",
    task="play music",
    intent="spotify_play",
    action="spotify_play",
    object="music",
    references=["it"],
    resolved_references={
        "it": "music"
    },
    unresolved_references=[],
    confidence=0.88,
    reason="test",
)


result = bridge.resolve(
    raw_input="make it louder",
    follow_up=follow_up,
)


print(result)