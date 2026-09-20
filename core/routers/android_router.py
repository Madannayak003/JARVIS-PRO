"""Fast routes for simple Android Control commands."""

from __future__ import annotations


ANDROID_APP_COMMANDS = {
    "camera": "camera",
    "settings": "settings",
    "browser": "browser",
    "gallery": "gallery",
    "phone": "phone",
    "messages": "messages",
    "whatsapp": "WhatsApp",
    "contacts": "contacts",
    "calculator": "calculator",
    "youtube": "YouTube",
    "chrome": "Chrome",
    "google maps": "Google Maps",
    "phonepe": "PhonePe",
    "google pay": "Google Pay",
    "gpay": "Google Pay",
    "paytm": "Paytm",
}


PHONE_PREFIXES = (
    "open phone ",
    "open my phone ",
    "open android ",
    "open my android ",
    "open mobile ",
    "open my mobile ",
)

LAUNCH_PREFIXES = (
    "launch phone ",
    "launch my phone ",
    "launch android ",
    "launch my android ",
    "launch mobile ",
    "launch my mobile ",
)


def android_route(command):
    if not command:
        return None
    command = str(command).strip().casefold()
    if not command:
        return None
    if command in {"check adb", "adb status", "check android adb"}:
        return [{"action": "android_check_adb"}]
    if command in {
        "check phone", "check android", "check android phone", "check device",
        "check android device",
    }:
        return [{"action": "android_check_device"}]
    if command in {
        "android device info", "android device information", "phone information",
        "check android information",
    }:
        return [{"action": "android_device_info"}]
    for prefix in PHONE_PREFIXES:
        if command.startswith(prefix):
            target = command.removeprefix(prefix).strip()
            app = ANDROID_APP_COMMANDS.get(target)
            if app:
                return [{"action": "android_open_app", "app": app}]

    for prefix in LAUNCH_PREFIXES:
        if command.startswith(prefix):
            target = command.removeprefix(prefix).strip()
            if target:
                return [{"action": "android_launch_app", "app": target}]

    # Generic open/launch commands belong to the existing desktop/browser
    # routes and must never be intercepted by Android Control.
    return None
