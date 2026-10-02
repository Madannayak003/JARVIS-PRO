"""Focused tests for the Android HUD connection integration."""

import unittest
from pathlib import Path

from services.android import AdbClient, AndroidDeviceManager


class FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class WirelessRunner:
    def __init__(self):
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if command[1:3] == ["devices", "-l"]:
            return FakeCompleted(
                stdout=(
                    "List of devices attached\n"
                    "192.0.2.10:5555\tdevice product:a13nnxx model:SM_A135F "
                    "device:a13 transport_id:13\n"
                )
            )
        if command[1:] == ["connect", "192.0.2.10:5555"]:
            return FakeCompleted(stdout="connected to 192.0.2.10:5555\n")
        if command[1:] == ["disconnect", "192.0.2.10:5555"]:
            return FakeCompleted(stdout="disconnected 192.0.2.10:5555\n")
        return FakeCompleted()


class UsbRunner(WirelessRunner):
    def __call__(self, command, **kwargs):
        if command[1:3] == ["devices", "-l"]:
            self.calls.append((command, kwargs))
            return FakeCompleted(
                stdout=(
                    "List of devices attached\n"
                    "RZ8T5139PRD\tdevice product:a13nnxx model:SM_A135F "
                    "device:a13 transport_id:14\n"
                )
            )
        return super().__call__(command, **kwargs)


class AndroidHudConnectionTests(unittest.TestCase):
    def test_wireless_connect_and_disconnect_are_scoped_to_one_endpoint(self):
        runner = WirelessRunner()
        client = AdbClient(adb_path="fake-adb", runner=runner)

        connected = client.connect("192.0.2.10", 5555)
        disconnected = client.disconnect("192.0.2.10:5555")

        self.assertTrue(connected.ok)
        self.assertTrue(disconnected.ok)
        self.assertEqual(connected.command[1:], ("connect", "192.0.2.10:5555"))
        self.assertEqual(disconnected.command[1:], ("disconnect", "192.0.2.10:5555"))
        self.assertNotIn("-s", connected.command)
        self.assertNotIn("-s", disconnected.command)

    def test_wireless_status_reports_connection_type_endpoint_and_model(self):
        manager = AndroidDeviceManager(
            AdbClient(adb_path="fake-adb", runner=WirelessRunner())
        )

        status = manager.connection_status()

        self.assertTrue(status.connected)
        self.assertEqual(status.connection_type, "Wireless")
        self.assertEqual(status.endpoint, "192.0.2.10:5555")
        self.assertEqual(status.model, "SM A135F")
        self.assertEqual(status.wireless_endpoints, ("192.0.2.10:5555",))

    def test_usb_status_reports_usb_without_an_endpoint(self):
        manager = AndroidDeviceManager(
            AdbClient(adb_path="fake-adb", runner=UsbRunner())
        )

        status = manager.connection_status()

        self.assertTrue(status.connected)
        self.assertEqual(status.connection_type, "USB")
        self.assertIsNone(status.endpoint)

    def test_hud_button_is_before_remote_and_uses_dashboard_api(self):
        page = Path("hud/web/app/page.tsx").read_text(encoding="utf-8")

        android_index = page.index('aria-label="Android device connection"')
        remote_index = page.index('onClick={openRemoteControl}')

        self.assertLess(android_index, remote_index)
        self.assertIn("●", page)
        self.assertIn("○", page)
        self.assertIn("/api/local/android/connect", page)
        self.assertIn("/api/local/android/disconnect", page)
        self.assertNotIn("subprocess", page.casefold())
        self.assertNotIn("adb.exe", page.casefold())

    def test_dashboard_exposes_only_scoped_android_connection_routes(self):
        server = Path("dashboard/server.py").read_text(encoding="utf-8")

        self.assertIn('"/api/local/android"', server)
        self.assertIn('"/api/local/android/connect"', server)
        self.assertIn('"/api/local/android/disconnect"', server)
        self.assertIn("manager.disconnect_wireless(endpoint)", server)
        self.assertNotIn('run_adb(["kill-server"])', server)

    def test_hud_eventsource_subscription_is_stable_and_deduplicated(self):
        page = Path("hud/web/app/page.tsx").read_text(encoding="utf-8")
        bridge = Path("hud/web/lib/hudBridge.ts").read_text(encoding="utf-8")

        self.assertIn("const handleHUDState = useCallback", page)
        self.assertIn("[applyPhoneCallState, handleHUDState]", page)
        self.assertNotIn("}, [hudState.system]);", page)
        self.assertEqual(page.count("new HUDBridge("), 1)
        self.assertIn("if (this.source !== source)", bridge)
        self.assertIn("phoneCallStatesEqual", page)
        self.assertIn("hudStatesEqual", page)

    def test_disconnected_phone_call_cannot_be_resurrected_by_stale_hud_state(self):
        page = Path("hud/web/app/page.tsx").read_text(encoding="utf-8")

        self.assertIn("phoneCallDismissedRef", page)
        self.assertIn("phoneCallExitTokenRef", page)
        self.assertIn("stale DISCONNECTED snapshot", page)
        self.assertIn("phoneCallDismissedRef.current = true", page)
        self.assertIn("if (exitToken !== phoneCallExitTokenRef.current)", page)


if __name__ == "__main__":
    unittest.main()
