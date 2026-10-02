"""Focused tests for additive local/private-network ADB transport support."""

import os
import unittest
from unittest.mock import patch

from services.android import AdbClient, AndroidDeviceManager


class FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class RemoteRunner:
    def __init__(self, endpoint="100.64.0.10:5555"):
        self.endpoint = endpoint
        self.calls = []
        self.connected = False

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if command[-2:] == ["devices", "-l"]:
            serial = self.endpoint if self.connected else ""
            rows = f"{serial}\tdevice model:VPN_PHONE\n" if serial else ""
            return FakeCompleted(stdout=f"List of devices attached\n{rows}")
        if command[1:2] == ["connect"]:
            self.connected = True
            return FakeCompleted(stdout=f"connected to {self.endpoint}\n")
        return FakeCompleted(stdout="JARVIS\n")


class AndroidRemoteNetworkTests(unittest.TestCase):
    def test_usb_is_preferred_over_wireless(self):
        runner = RemoteRunner()

        def devices(command, **kwargs):
            runner.calls.append((command, kwargs))
            if command[-2:] == ["devices", "-l"]:
                return FakeCompleted(
                    stdout=(
                        "List of devices attached\n"
                        "100.64.0.10:5555\tdevice model:VPN_PHONE\n"
                        "USB123\tdevice model:USB_PHONE\n"
                    )
                )
            return FakeCompleted()

        client = AdbClient(adb_path="fake-adb", runner=devices)
        self.assertEqual(client.select_device().serial, "USB123")

    def test_auto_uses_existing_local_wireless_when_usb_is_missing(self):
        runner = RemoteRunner()
        runner.connected = True
        with patch.dict(os.environ, {"ANDROID_REMOTE_HOST": ""}, clear=False):
            client = AdbClient(adb_path="fake-adb", runner=runner)
            self.assertEqual(client.select_device().serial, "100.64.0.10:5555")

    def test_remote_mode_does_not_select_a_local_wireless_device(self):
        runner = RemoteRunner()
        runner.connected = True
        with patch.dict(
            os.environ,
            {
                "ANDROID_CONNECTION_MODE": "REMOTE",
                "ANDROID_REMOTE_HOST": "100.64.0.10",
            },
            clear=False,
        ):
            client = AdbClient(adb_path="fake-adb", runner=runner)
            self.assertEqual(client.select_device().serial, "100.64.0.10:5555")

    def test_configured_remote_endpoint_is_used_without_scanning(self):
        runner = RemoteRunner()
        with patch.dict(
            os.environ,
            {
                "ANDROID_CONNECTION_MODE": "AUTO",
                "ANDROID_REMOTE_HOST": "100.64.0.10",
                "ANDROID_REMOTE_PORT": "5555",
            },
            clear=False,
        ):
            client = AdbClient(adb_path="fake-adb", runner=runner)
            selected = client.select_device()

        self.assertEqual(selected.serial, "100.64.0.10:5555")
        self.assertEqual(
            [call[0][1] for call in runner.calls if len(call[0]) > 1 and call[0][1] == "connect"],
            ["connect"],
        )
        self.assertEqual(client.connection_type(selected), "REMOTE")

    def test_missing_remote_configuration_does_not_attempt_network(self):
        runner = RemoteRunner()
        with patch.dict(
            os.environ,
            {
                "ANDROID_CONNECTION_MODE": "AUTO",
                "ANDROID_REMOTE_HOST": "",
                "ANDROID_REMOTE_PORT": "5555",
            },
            clear=False,
        ):
            client = AdbClient(adb_path="fake-adb", runner=runner)
            self.assertIsNone(client.select_device())

        self.assertFalse(any("connect" in call[0] for call in runner.calls))

    def test_remote_failure_is_clean_and_does_not_scan(self):
        class FailedRunner(RemoteRunner):
            def __call__(self, command, **kwargs):
                self.calls.append((command, kwargs))
                if command[-2:] == ["devices", "-l"]:
                    return FakeCompleted(stdout="List of devices attached\n")
                if command[1:2] == ["connect"]:
                    return FakeCompleted(returncode=1, stderr="failed to connect")
                return FakeCompleted()

        runner = FailedRunner()
        with patch.dict(os.environ, {"ANDROID_REMOTE_HOST": "100.64.0.10"}, clear=False):
            client = AdbClient(adb_path="fake-adb", runner=runner)
            self.assertIsNone(client.select_device())

        connect_calls = [call for call in runner.calls if call[0][1:2] == ["connect"]]
        self.assertEqual(len(connect_calls), 1)
        self.assertNotIn("scan", " ".join(" ".join(call[0]) for call in runner.calls).casefold())

    def test_tailscale_is_not_a_dependency(self):
        with patch.dict(os.environ, {"ANDROID_REMOTE_HOST": ""}, clear=False):
            client = AdbClient(adb_path="fake-adb", runner=RemoteRunner())
        self.assertIsNone(client.remote_endpoint)


if __name__ == "__main__":
    unittest.main()
