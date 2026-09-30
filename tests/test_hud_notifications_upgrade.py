def test_structured_notification_preserves_event_contract(monkeypatch):
    import hud.integration as integration

    events = []
    monkeypatch.setattr(integration.HUDEmitter, "emit", lambda event, data: events.append((event, data)))

    integration.HUDIntegration.notify("REMINDER", "Call Mom", level="REMINDER", source="reminder", metadata={"id": 3})

    assert events[-1][0] == integration.HUDEvent.NOTIFICATION
    assert events[-1][1]["title"] == "REMINDER"
    assert events[-1][1]["message"] == "Call Mom"
    assert events[-1][1]["metadata"]["id"] == 3


def test_notification_failure_is_swallowed(monkeypatch):
    import hud.integration as integration

    monkeypatch.setattr(integration.HUDEmitter, "emit", lambda *_args: (_ for _ in ()).throw(RuntimeError("HUD offline")))
    integration.HUDIntegration.notify("INFO", "safe")
