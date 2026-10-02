"""Focused tests for private-network Dashboard QR advertisement."""

import os
import sys
import types
import unittest
from unittest.mock import patch


def _install_optional_dependency_stubs():
    """Keep this focused test independent of optional voice/AI packages."""
    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda *args, **kwargs: True
    sys.modules["dotenv"] = dotenv

    interrupt = types.ModuleType("core.interrupt")
    interrupt.interrupt = lambda *args, **kwargs: None
    sys.modules["core.interrupt"] = interrupt

    runtime = types.ModuleType("core.runtime")
    runtime.handle_priority = lambda *args, **kwargs: False
    sys.modules["core.runtime"] = runtime

    ai_service = types.ModuleType("ai.core.service")
    ai_service.ai_service = object()
    sys.modules["ai.core.service"] = ai_service

    chat_api = types.ModuleType("chatbot.ai_chat_api")
    for name in ("create_chat", "list_chats", "get_chat", "delete_chat", "rename_chat", "send_message", "get_model", "set_model"):
        setattr(chat_api, name, lambda *args, **kwargs: None)
    sys.modules["chatbot.ai_chat_api"] = chat_api

    windows = types.ModuleType("tools.windows_integration")
    windows.create_desktop_shortcut = lambda *args, **kwargs: None
    windows.get_autostart_status = lambda *args, **kwargs: False
    windows.set_autostart = lambda *args, **kwargs: None
    sys.modules["tools.windows_integration"] = windows

    listener = types.ModuleType("core.listener")
    for name in ("start_listener", "pause_listener", "resume_listener", "listener_running", "listener_paused"):
        setattr(listener, name, lambda *args, **kwargs: False)
    sys.modules["core.listener"] = listener


try:
    from dashboard.server import DashboardServer
except ModuleNotFoundError:
    _install_optional_dependency_stubs()
    from dashboard.server import DashboardServer


class DashboardPrivateNetworkTests(unittest.TestCase):
    def test_pairing_url_uses_explicit_private_vpn_host(self):
        server = DashboardServer.__new__(DashboardServer)
        server.ip = "192.168.1.20"
        server.port = 8765
        server._pin = "ABC234"
        with patch.dict(os.environ, {"JARVIS_REMOTE_HOST": "100.64.0.20"}, clear=False):
            self.assertEqual(
                server.pairing_url(),
                "http://100.64.0.20:8765/login?pin=ABC234",
            )

    def test_pairing_url_preserves_existing_local_default(self):
        server = DashboardServer.__new__(DashboardServer)
        server.ip = "192.168.1.20"
        server.port = 8765
        server._pin = "ABC234"
        with patch.dict(os.environ, {"JARVIS_REMOTE_HOST": ""}, clear=False):
            self.assertEqual(
                server.pairing_url(),
                "http://192.168.1.20:8765/login?pin=ABC234",
            )


if __name__ == "__main__":
    unittest.main()
