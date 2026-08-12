from hud.manager import hud
from hud.bus import hud_bus


def on_hud_event(event):

    print(
        "[HUD EVENT]",
        event.name,
        event.data
    )


hud_bus.subscribe(
    on_hud_event
)


print()
print("=== HUD FOUNDATION TEST ===")
print()


hud.listening()

hud.thinking()

hud.ai_model(
    "ollama",
    "jarvis"
)

hud.voice_mode(
    "offline"
)

hud.executing(
    "developer generator"
)

hud.task_finished(
    "developer generator"
)

hud.system_update(
    {
        "cpu": 25,
        "ram": 48,
        "battery": 87,
    }
)

hud.notify(
    "HUD foundation is working."
)

hud.idle()


print()
print("=== FINAL HUD STATE ===")
print()

print(
    hud.state
)