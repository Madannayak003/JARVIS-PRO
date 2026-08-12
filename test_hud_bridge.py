from core.hud_bridge import hud_bridge
from hud.bus import hud_bus


def on_event(event):

    print(
        "[REAL HUD BRIDGE EVENT]",
        event.name,
        event.data
    )


hud_bus.subscribe(
    on_event
)


print()
print("=== HUD BRIDGE TEST ===")
print()


hud_bridge.listening()

hud_bridge.thinking()

hud_bridge.voice_mode(
    "online"
)

hud_bridge.ai_model(
    "gemini",
    "gemini-3.6-flash"
)

hud_bridge.task_started(
    "chat"
)

hud_bridge.executing(
    "chat"
)

hud_bridge.task_finished(
    "chat"
)

hud_bridge.system_update(
    {
        "cpu": 20,
        "ram": 45,
        "battery": 88,
    }
)

hud_bridge.notify(
    "JARVIS HUD bridge connected."
)

hud_bridge.idle()


print()
print("=== BRIDGE TEST COMPLETE ===")
print()