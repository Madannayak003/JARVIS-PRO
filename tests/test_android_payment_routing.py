"""Focused tests for the Android bridge command boundaries."""

import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch

from core.routers.android_router import android_route
from core.routers.browser_router import browser_route
from core.routers.payment_router import payment_route
from core.routers.vision_router import vision_route
import services.android.adb_client as adb_client_module
from services.android import AdbClient, AndroidDeviceManager


class FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class FakeRunner:
    def __init__(self):
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if command[-2:] == ["devices", "-l"]:
            return FakeCompleted(
                stdout=(
                    "List of devices attached\n"
                    "RZ8T5139PRD\tdevice product:a13nnxx model:SM_A135F "
                    "device:a13 transport_id:13\n"
                )
            )
        if "pm" in command and "list" in command:
            return FakeCompleted(
                stdout=(
                    "package:com.phonepe.app\n"
                    "package:com.google.android.apps.nbu.paisa.user\n"
                )
            )
        if "resolve-activity" in command:
            if "com.google.android.apps.nbu.paisa.user" in command:
                return FakeCompleted(
                    stdout=(
                        "priority=0\n"
                        "com.google.android.apps.nbu.paisa.user/.LauncherActivity\n"
                    )
                )
            return FakeCompleted(stdout="priority=0\ncom.phonepe.app/.MainActivity\n")
        if "am" in command and "start" in command:
            return FakeCompleted(
                stdout="Warning: Activity not started, intent has been delivered.\n"
            )
        return FakeCompleted()


class AndroidBridgeTests(unittest.TestCase):
    def test_adb_uses_argument_lists_and_parses_devices(self):
        runner = FakeRunner()
        client = AdbClient(adb_path="fake-adb", runner=runner)

        devices = client.get_devices()

        self.assertEqual(devices[0].serial, "RZ8T5139PRD")
        self.assertEqual(devices[0].model, "SM A135F")
        self.assertFalse(runner.calls[0][1]["shell"])

    def test_adb_uses_no_console_creation_flag_on_windows(self):
        runner = FakeRunner()
        client = AdbClient(adb_path="fake-adb", runner=runner)

        with patch.object(adb_client_module.os, "name", "nt"):
            client.run_adb(["version"])

        self.assertEqual(
            runner.calls[0][1]["creationflags"],
            getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
        )

    def test_adb_does_not_pass_windows_creation_flag_on_non_windows(self):
        runner = FakeRunner()
        client = AdbClient(adb_path="fake-adb", runner=runner)

        with patch.object(adb_client_module.os, "name", "posix"):
            client.run_adb(["version"])

        self.assertNotIn("creationflags", runner.calls[0][1])

    def test_package_resolution_only_returns_installed_apps(self):
        runner = FakeRunner()
        client = AdbClient(adb_path="fake-adb", device_id="RZ8T5139PRD", runner=runner)
        manager = AndroidDeviceManager(client)

        self.assertEqual(manager.resolve_package("PhonePe"), "com.phonepe.app")
        self.assertEqual(
            manager.resolve_package("Google Pay"),
            "com.google.android.apps.nbu.paisa.user",
        )
        self.assertIsNone(manager.resolve_package("Paytm"))

    def test_android_commands_are_separate_from_payment_commands(self):
        self.assertIsNone(android_route("open camera"))
        self.assertEqual(vision_route("open camera"), [{"action": "camera_preview"}])
        self.assertIsNone(android_route("open settings"))
        self.assertEqual(browser_route("open settings"), [{"action": "open", "app": "settings"}])
        self.assertIsNone(android_route("open Chrome"))
        self.assertEqual(browser_route("open chrome"), [{"action": "open", "app": "chrome"}])
        self.assertIsNone(android_route("open YouTube"))
        self.assertEqual(browser_route("open youtube"), [{"action": "open", "app": "youtube"}])
        self.assertEqual(
            android_route("open phone Chrome"),
            [{"action": "android_open_app", "app": "Chrome"}],
        )
        self.assertEqual(
            android_route("open my phone camera"),
            [{"action": "android_open_app", "app": "camera"}],
        )
        self.assertEqual(
            android_route("open android settings"),
            [{"action": "android_open_app", "app": "settings"}],
        )
        self.assertEqual(
            android_route("open phone YouTube"),
            [{"action": "android_open_app", "app": "YouTube"}],
        )
        self.assertEqual(
            payment_route("make payment using PhonePe"),
            [{"action": "make_payment", "payment_app": "PhonePe"}],
        )
        self.assertEqual(payment_route("make payment"), [{"action": "make_payment"}])

    def test_payment_launch_uses_discovered_packages(self):
        runner = FakeRunner()
        client = AdbClient(adb_path="fake-adb", device_id="RZ8T5139PRD", runner=runner)
        manager = AndroidDeviceManager(client)

        phonepe = manager.open_app("PhonePe")
        google_pay = manager.open_app("Google Pay")

        self.assertTrue(phonepe.success)
        self.assertEqual(phonepe.package, "com.phonepe.app")
        self.assertTrue(google_pay.success)
        self.assertEqual(google_pay.package, "com.google.android.apps.nbu.paisa.user")
        launch_commands = [call[0] for call in runner.calls if "am" in call[0]]
        self.assertIn("-n", launch_commands[0])
        self.assertIn("com.phonepe.app/.MainActivity", launch_commands[0])
        self.assertIn("-n", launch_commands[1])
        self.assertIn(
            "com.google.android.apps.nbu.paisa.user/.LauncherActivity",
            launch_commands[1],
        )

    def test_unavailable_requested_payment_app_is_not_replaced(self):
        runner = FakeRunner()
        client = AdbClient(adb_path="fake-adb", device_id="RZ8T5139PRD", runner=runner)
        result = AndroidDeviceManager(client).open_app("Paytm")

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "not_installed")
        self.assertIsNone(result.package)

    def test_payment_skill_contains_no_transaction_automation(self):
        source = Path("skills/payments/payments.py").read_text(encoding="utf-8").casefold()
        for forbidden in ("cv2", "input text", "input keyevent", "uiautomator", "click pay"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
