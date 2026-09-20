"""Focused tests for the dedicated Phone Call skill."""

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from core.routers.phone_call_router import phone_call_route
from services.android import AdbClient
import skills.phone_call.monitor as monitor_module
from skills.phone_call.monitor import (
    ACTIVE,
    DISCONNECTED,
    IDLE,
    RINGING,
    CallSnapshot,
    PhoneCallMonitor,
    parse_telephony_registry,
)


def _load_phone_skill_without_optional_ai_dependencies():
    """Load the skill with only its registry seam stubbed for this test file."""
    existing = sys.modules.get("core.registry")
    if existing is None:
        registry = types.ModuleType("core.registry")
        registry.register = lambda *args, **kwargs: None
        sys.modules["core.registry"] = registry
    try:
        from skills.phone_call import phone_call

        return phone_call
    finally:
        if existing is None:
            sys.modules.pop("core.registry", None)


phone_call = _load_phone_skill_without_optional_ai_dependencies()


class FakeManager:
    def __init__(self):
        self.intents = []

    def launch_intent(self, intent):
        self.intents.append(intent)
        return True


class PhoneCallTests(unittest.TestCase):
    def tearDown(self):
        from core.confirmation import clear

        clear()

    def test_skill_helpers_load_and_normalize_number(self):
        self.assertEqual(
            phone_call.normalize_phone_number(" +91 (98765) 43210 "),
            "+919876543210",
        )
        self.assertEqual(phone_call.normalize_phone_number("00919876543210"), "+919876543210")
        self.assertIsNone(phone_call.normalize_phone_number("12345"))
        self.assertIsNone(phone_call.normalize_phone_number("98765abc210"))

    def test_samsung_provider_row_parser_is_column_order_independent(self):
        output = (
            "Row: 249 creation_time=1, data4=+917795330370, data1=7795330370, "
            "sec_preferred_sim=NULL, display_name=MOTHER INDIA ❤️✨️, "
            "data_sync1=NULL, contact_id=123\n"
        )
        self.assertEqual(
            phone_call._parse_phone_contacts(output),
            [
                {
                    "name": "MOTHER INDIA ❤️✨️",
                    "number": "7795330370",
                    "normalized_number": "+917795330370",
                    "contact_id": "123",
                }
            ],
        )

    def test_contact_matching_supports_partial_names_and_relationship_aliases(self):
        phone_call.query_phone_contacts = lambda: [
            {
                "name": "MOTHER INDIA",
                "number": "7795330370",
                "normalized_number": "+917795330370",
                "contact_id": "123",
            }
        ]
        for query in ("MOTHER INDIA", "mother india", "mother", "mom", "my mom"):
            value = query.removeprefix("my ")
            matches = phone_call._find_contact(value)
            self.assertEqual(len(matches), 1, query)
            self.assertEqual(matches[0]["name"], "MOTHER INDIA")

    def test_contact_matching_is_ambiguous_for_multiple_token_matches(self):
        phone_call.query_phone_contacts = lambda: [
            {"name": "MOTHER INDIA", "number": "7795330370"},
            {"name": "MOTHER HOME", "number": "7795330371"},
        ]
        self.assertEqual(len(phone_call._find_contact("mother")), 2)

    def test_relationship_alias_prefers_mother_before_amma_fallback(self):
        phone_call.query_phone_contacts = lambda: [
            {"name": "MOTHER INDIA", "number": "7795330370"},
            {"name": "Amma", "number": "9241264742"},
            {"name": "Bhagya Amma", "number": "9900947380"},
        ]
        matches = phone_call._find_contact("mom")
        self.assertEqual([item["name"] for item in matches], ["MOTHER INDIA"])

    def test_call_number_and_contact_routes(self):
        self.assertEqual(phone_call_route("call status"), [{"action": "call_status"}])
        self.assertEqual(phone_call_route("answer call"), [{"action": "answer_call"}])
        self.assertEqual(phone_call_route("reject call"), [{"action": "reject_call"}])
        self.assertEqual(phone_call_route("hang up"), [{"action": "end_call"}])
        self.assertEqual(
            phone_call_route("show missed calls"),
            [{"action": "missed_calls"}],
        )
        self.assertEqual(
            phone_call_route("call 9876543210"),
            [{"action": "phone_call_number", "phone_number": "9876543210"}],
        )
        self.assertEqual(
            phone_call_route("dial Rahul"),
            [{"action": "phone_call_contact", "contact_name": "rahul"}],
        )
        self.assertEqual(
            phone_call_route("call Rahul now"),
            [{"action": "phone_call_contact", "contact_name": "rahul"}],
        )
        self.assertEqual(
            phone_call_route("call my mom"),
            [{"action": "phone_call_contact", "contact_name": "mom"}],
        )
        self.assertEqual(
            phone_call_route("make a phone call to Mom"),
            [{"action": "phone_call_contact", "contact_name": "mom"}],
        )
        self.assertEqual(
            phone_call_route("call this number +919876543210"),
            [{"action": "phone_call_number", "phone_number": "+919876543210"}],
        )
        self.assertEqual(
            phone_call_route("call 12345"),
            [{"action": "phone_call_number", "phone_number": "12345"}],
        )

    def test_contact_safety_and_existing_confirmation(self):
        messages = []
        phone_call._say = messages.append
        phone_call.query_phone_contacts = lambda: [
            {"name": "Rahul", "number": "+919876543210"},
            {"name": "Rahul", "number": "+919876543211"},
        ]
        self.assertFalse(phone_call.phone_call_contact({"contact_name": "Rahul"}))
        self.assertIn("Which one", messages[-1])

        phone_call.query_phone_contacts = lambda: []
        self.assertFalse(phone_call.phone_call_contact({"contact_name": "Nobody"}))
        self.assertIn("couldn't find", messages[-1])

    def test_contact_starts_call_with_documented_call_intent(self):
        messages = []
        manager = FakeManager()
        phone_call._say = messages.append
        phone_call.query_phone_contacts = lambda: [
            {"name": "Rahul", "number": "+919876543210"},
        ]
        phone_call.get_android_manager = lambda: manager

        self.assertTrue(phone_call.phone_call_contact({"contact_name": "Rahul"}))
        self.assertEqual(manager.intents[0].action, "android.intent.action.CALL")
        self.assertEqual(manager.intents[0].data, "tel:+919876543210")
        self.assertIn("Calling Rahul.", messages)

    def test_direct_number_starts_call_and_falls_back_to_dialer(self):
        messages = []
        manager = FakeManager()
        manager.launch_intent = lambda intent: manager.intents.append(intent) or intent.action.endswith(".DIAL")
        phone_call._say = messages.append
        phone_call.get_android_manager = lambda: manager

        self.assertTrue(phone_call.phone_call_number({"phone_number": "+919876543210"}))
        self.assertEqual(
            [intent.action for intent in manager.intents],
            ["android.intent.action.CALL", "android.intent.action.DIAL"],
        )
        self.assertIn("The dialer is ready. Please press Call.", messages)

    def test_call_state_machine_announces_once_and_tracks_transitions(self):
        announcements = []
        notifications = []
        monitor = PhoneCallMonitor(
            manager=object(),
            announce=announcements.append,
            notify=notifications.append,
        )
        monitor._resolve_caller = lambda number: "Rahul"

        self.assertEqual(
            monitor.process_snapshot(CallSnapshot(RINGING, "+919876543210")).state,
            RINGING,
        )
        monitor.process_snapshot(CallSnapshot(RINGING, "+919876543210"))
        self.assertEqual(len(announcements), 1)
        self.assertEqual(
            monitor.process_snapshot(CallSnapshot(ACTIVE, "+919876543210")).state,
            ACTIVE,
        )
        self.assertEqual(
            monitor.process_snapshot(CallSnapshot(IDLE)).state,
            DISCONNECTED,
        )
        self.assertEqual(monitor.status_message(), "Call ended.")
        self.assertEqual(monitor.process_snapshot(CallSnapshot(IDLE)).state, IDLE)
        self.assertTrue(any("INCOMING CALL" in message for message in notifications))

    def test_outgoing_active_disconnected_state_and_structured_data(self):
        notifications = []
        monitor = PhoneCallMonitor(
            manager=object(),
            announce=lambda message: None,
            notify=notifications.append,
        )

        outgoing = monitor.begin_outgoing("+919876543210", "Rahul")
        self.assertEqual(outgoing.state, "OUTGOING")
        self.assertEqual(outgoing.direction, "OUTGOING")
        self.assertTrue(outgoing.started_at)

        active = monitor.process_snapshot(CallSnapshot(ACTIVE, "+919876543210"))
        self.assertEqual(active.state, ACTIVE)
        self.assertEqual(active.direction, "OUTGOING")
        self.assertTrue(active.active_started_at)

        monitor.process_snapshot(CallSnapshot(ACTIVE, "+919876543210"))
        self.assertEqual(len([item for item in notifications if "active" in item.casefold()]), 1)

        ended = monitor.process_snapshot(CallSnapshot(IDLE))
        self.assertEqual(ended.state, DISCONNECTED)
        self.assertEqual(ended.caller_name, "Rahul")
        self.assertIn("Call ended", notifications[-1])

    def test_outgoing_transient_idle_keeps_calling_until_active(self):
        notifications = []
        monitor = PhoneCallMonitor(
            manager=object(),
            announce=lambda message: None,
            notify=notifications.append,
        )

        monitor.begin_outgoing("+919876543210", "Rahul")
        transient = monitor.process_snapshot(CallSnapshot(IDLE))
        self.assertEqual(transient.state, "OUTGOING")
        self.assertFalse(any("Call ended" in message for message in notifications))

        active = monitor.process_snapshot(CallSnapshot(ACTIVE))
        self.assertEqual(active.state, ACTIVE)
        self.assertEqual(active.direction, "OUTGOING")
        self.assertFalse(any("Call ended" in message for message in notifications))

    def test_outgoing_idle_beyond_grace_becomes_disconnected(self):
        notifications = []
        monitor = PhoneCallMonitor(
            manager=object(),
            announce=lambda message: None,
            notify=notifications.append,
        )

        monitor.begin_outgoing("+919876543210", "Rahul")
        with patch.object(
            monitor_module.time,
            "monotonic",
            side_effect=(
                100.0,
                100.0 + monitor_module.OUTGOING_IDLE_GRACE_SECONDS + 0.01,
                100.0 + monitor_module.OUTGOING_IDLE_GRACE_SECONDS + 0.01,
            ),
        ):
            self.assertEqual(monitor.process_snapshot(CallSnapshot(IDLE)).state, "OUTGOING")
            ended = monitor.process_snapshot(CallSnapshot(IDLE))

        self.assertEqual(ended.state, DISCONNECTED)
        self.assertEqual(ended.direction, "OUTGOING")
        self.assertIn("Call ended", notifications[-1])

    def test_hud_state_event_contains_structured_call_payload(self):
        events = []
        fake_hud_module = types.ModuleType("hud.integration")

        class FakeHUDIntegration:
            @staticmethod
            def system_activity(message):
                pass

            @staticmethod
            def system_update(data):
                events.append(data)

        fake_hud_module.HUDIntegration = FakeHUDIntegration
        monitor = PhoneCallMonitor(
            manager=object(),
            announce=lambda message: None,
            notify=lambda message: None,
        )
        with patch.dict(sys.modules, {"hud.integration": fake_hud_module}):
            monitor.begin_outgoing("+919876543210", "Rahul")

        payload = events[-1]["phone_call"]
        self.assertEqual(payload["type"], "PHONE_CALL_STATUS")
        self.assertEqual(payload["state"], "outgoing")
        self.assertEqual(payload["direction"], "OUTGOING")
        self.assertEqual(payload["caller_name"], "Rahul")
        self.assertTrue(payload["started_at"])

    def test_unknown_incoming_number_uses_number_without_guessing_name(self):
        announcements = []
        monitor = PhoneCallMonitor(
            manager=object(),
            announce=announcements.append,
            notify=lambda message: None,
        )
        monitor._resolve_caller = lambda number: ""
        monitor.process_snapshot(CallSnapshot(RINGING, "+919876543210"))
        self.assertEqual(
            announcements,
            ["You have an incoming call from +919876543210."],
        )

    def test_utf8_subprocess_capture_is_explicit(self):
        calls = []

        class EncodingRunner:
            def __call__(self, command, **kwargs):
                calls.append(kwargs)
                return type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        AdbClient(adb_path="fake-adb", runner=EncodingRunner()).get_devices()
        self.assertEqual(calls[0]["encoding"], "utf-8")
        self.assertEqual(calls[0]["errors"], "replace")

    def test_telephony_parser_uses_read_only_state_fields(self):
        snapshot = parse_telephony_registry(
            "mCallState=0\n"
            "mCallState=1\n"
            "mCallIncomingNumber=+919876543210\n"
        )
        self.assertEqual(snapshot.state, RINGING)
        self.assertEqual(snapshot.phone_number, "+919876543210")

    def test_monitor_tolerates_disconnect_and_stops_cleanly(self):
        class DisconnectedManager:
            class Adb:
                @staticmethod
                def select_device():
                    return None

            adb = Adb()

        monitor = PhoneCallMonitor(
            manager=DisconnectedManager(),
            poll_interval=0.01,
            announce=lambda message: None,
            notify=lambda message: None,
        )
        self.assertEqual(monitor.poll_once().state, IDLE)
        self.assertTrue(monitor.start())
        monitor.stop()
        self.assertFalse(monitor.running)

    def test_unsupported_controls_are_manual_fallbacks(self):
        source = Path("skills/phone_call").joinpath("phone_call.py").read_text(encoding="utf-8").casefold()
        for forbidden in ("input keyevent", "uiautomator", "input text", "tap ", "cv2", "root"):
            self.assertNotIn(forbidden, source)
        self.assertIn("not safely available", source)


if __name__ == "__main__":
    unittest.main()
