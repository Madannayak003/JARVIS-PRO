"""Focused tests for Remote Control/HUD activity synchronization."""

import asyncio
import sys
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


def _install_optional_dependency_stubs():
    """Keep these unit tests runnable in a minimal checkout."""

    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda *args, **kwargs: None
    sys.modules.setdefault("dotenv", dotenv)

    runtime = types.ModuleType("core.runtime")
    runtime.handle_priority = lambda text: False
    sys.modules.setdefault("core.runtime", runtime)

    chat_api = types.ModuleType("chatbot.ai_chat_api")
    for name in (
        "create_chat",
        "list_chats",
        "get_chat",
        "delete_chat",
        "rename_chat",
        "send_message",
        "get_model",
        "set_model",
    ):
        setattr(chat_api, name, lambda *args, **kwargs: None)
    sys.modules.setdefault("chatbot.ai_chat_api", chat_api)

    windows = types.ModuleType("tools.windows_integration")
    windows.get_autostart_status = lambda: False
    windows.set_autostart = lambda *args, **kwargs: None
    sys.modules.setdefault("tools.windows_integration", windows)

    listener = types.ModuleType("core.listener")
    for name in (
        "start_listener",
        "pause_listener",
        "resume_listener",
        "listener_running",
        "listener_paused",
    ):
        setattr(listener, name, lambda *args, **kwargs: False)
    sys.modules.setdefault("core.listener", listener)


try:
    from dashboard.server import DashboardServer
except ModuleNotFoundError:
    _install_optional_dependency_stubs()
    from dashboard.server import DashboardServer

from hud.events import (
    HUDEvent,
    HUD_COMMAND,
    HUD_SYSTEM_ACTIVITY,
)
from hud.bus import hud_bus
from hud.integration import HUDIntegration


class RemoteEventSyncTests(unittest.TestCase):

    @staticmethod
    def make_server():
        server = DashboardServer.__new__(DashboardServer)
        server._history = []
        server._history_event_ids = set()
        server._history_lock = threading.Lock()
        server._clients = set()
        server._loop = None
        return server

    def test_user_and_system_hud_events_keep_identity(self):
        server = self.make_server()
        server._broadcast_threadsafe = Mock()

        user_event = HUDEvent(
            name=HUD_COMMAND,
            data={"text": "open website list"},
            source="remote_control",
        )
        system_event = HUDEvent(
            name=HUD_SYSTEM_ACTIVITY,
            data={"message": "Personal websites requested."},
        )

        server._on_hud_event(user_event)
        server._on_hud_event(system_event)

        calls = [call.args[0] for call in server._broadcast_threadsafe.call_args_list]
        self.assertEqual(calls[0]["type"], "log")
        self.assertEqual(calls[0]["speaker"], "user")
        self.assertEqual(calls[0]["event_id"], user_event.event_id)
        self.assertEqual(calls[0]["source"], "remote_control")
        self.assertEqual(calls[1]["type"], "sys")
        self.assertEqual(calls[1]["text"], "Personal websites requested.")
        self.assertEqual(calls[1]["event_id"], system_event.event_id)
        self.assertNotEqual(calls[0]["event_id"], calls[1]["event_id"])

    def test_same_event_id_is_recorded_once_but_same_text_is_not_deduplicated(self):
        server = self.make_server()

        first = {
            "type": "log",
            "speaker": "user",
            "text": "what time is it",
            "event_id": "event-1",
        }
        second = {
            **first,
            "event_id": "event-2",
        }

        asyncio.run(server.broadcast(first))
        asyncio.run(server.broadcast(first))
        asyncio.run(server.broadcast(second))

        self.assertEqual([item["event_id"] for item in server._history], ["event-1", "event-2"])

    def test_remote_command_enters_normal_pipeline_once(self):
        server = self.make_server()
        server.command_handler = Mock(return_value="Found 5 configured personal websites.")
        server._broadcast_threadsafe = Mock()

        live = types.ModuleType("voice.live_conversation")
        live.live_conversation_status = lambda: False
        live.send_live_text = Mock(return_value=False)

        with patch.dict(sys.modules, {"voice.live_conversation": live}), patch(
            "dashboard.server.handle_priority", return_value=False
        ), patch("dashboard.server.HUDIntegration.command") as hud_command:
            server._run_command("open website list")

        hud_command.assert_called_once_with(
            "open website list",
            source="remote_control",
        )
        server.command_handler.assert_called_once_with("open website list")
        server._broadcast_threadsafe.assert_not_called()

    def test_remote_token_authorization_still_accepts_valid_login_session(self):
        server = self.make_server()
        server._tokens = {"valid-token"}
        request = Mock()
        request.headers = {
            "authorization": "Bearer valid-token",
        }

        self.assertEqual(server._get_token(request), "valid-token")

    def test_hud_integration_attaches_source_and_stable_id(self):
        received = []

        def collect(event):
            if event.name == HUD_COMMAND:
                received.append(event)

        hud_bus.subscribe(collect)
        try:
            HUDIntegration.command(
                "open website list",
                source="remote_control",
            )
        finally:
            hud_bus.unsubscribe(collect)

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].source, "remote_control")
        self.assertTrue(received[0].event_id)

    def test_response_is_projected_from_existing_voice_output_event(self):
        server = self.make_server()
        server._broadcast_threadsafe = Mock()

        with patch("dashboard.server.HUDIntegration.response") as hud_response:
            server._on_voice_output("Found 5 configured personal websites.")

        hud_response.assert_called_once()
        server._broadcast_threadsafe.assert_not_called()

    def test_identical_commands_at_different_times_are_distinct_events(self):
        server = self.make_server()
        server._broadcast_threadsafe = Mock()

        for _ in range(2):
            server._on_hud_event(
                HUDEvent(
                    name=HUD_COMMAND,
                    data={"text": "what time is it"},
                    source="remote_control",
                )
            )

        ids = [
            call.args[0]["event_id"]
            for call in server._broadcast_threadsafe.call_args_list
        ]
        self.assertEqual(len(ids), 2)
        self.assertNotEqual(ids[0], ids[1])

    def test_remote_client_uses_authoritative_events_and_event_ids(self):
        html = (
            Path(__file__).resolve().parents[1]
            / "dashboard"
            / "static"
            / "app.html"
        ).read_text(encoding="utf-8")

        self.assertIn("const seenEventIds = new Set();", html)
        self.assertIn('type === "sys"', html)
        self.assertIn('label.textContent =\n            "SYS";', html)
        self.assertNotIn(
            'addMessage(\n        "user",\n        text\n    );',
            html,
        )


if __name__ == "__main__":
    unittest.main()
