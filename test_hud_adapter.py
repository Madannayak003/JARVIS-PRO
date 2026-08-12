from hud import HUDAdapter
from hud.bus import hud_bus


def on_event(event):

    print(
        "[HUD ADAPTER EVENT]",
        event.name,
        event.data
    )


hud_bus.subscribe(
    on_event
)


print()
print("=== HUD ADAPTER TEST ===")
print()


HUDAdapter.listening()

HUDAdapter.thinking()

HUDAdapter.ai_model(
    "ollama",
    "jarvis"
)

HUDAdapter.voice_mode(
    "online"
)

HUDAdapter.task_started(
    "chat"
)

HUDAdapter.executing(
    "chat"
)

HUDAdapter.task_finished(
    "chat"
)

HUDAdapter.system_update(
    {
        "cpu": 31,
        "ram": 52,
        "battery": 91,
    }
)

HUDAdapter.notify(
    "Adapter connection test successful."
)

HUDAdapter.idle()


print()
print("=== TEST COMPLETE ===")
print()