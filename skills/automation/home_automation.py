"""
JARVIS PRO - Home Automation
Mark-L-main automation adapted for JARVIS PRO.

Place at:
    skills/automation/home_automation.py

This does NOT replace any existing JARVIS skill.
Set JARVIS_ESP32_IP in the environment instead of hard-coding
the ESP32 address.
"""

import os
import requests
from core.registry import register

HTTP_TIMEOUT = float(os.getenv("JARVIS_ESP32_TIMEOUT", "3"))
ESP32_IP = os.getenv("JARVIS_ESP32_IP", "").strip()
BASE_URL = f"http://{ESP32_IP}" if ESP32_IP else ""


def _endpoint(device: str, state: str) -> str:
    if not BASE_URL:
        raise RuntimeError(
            "JARVIS_ESP32_IP is not configured."
        )

    device = device.strip().lower()
    state = state.strip().upper()

    if device not in {"light", "fan"}:
        raise ValueError(
            f"Unsupported device: {device}. "
            "Currently supported: light, fan."
        )

    if state not in {"ON", "OFF"}:
        raise ValueError("State must be ON or OFF.")

    return f"{BASE_URL}/{device}/{state}"


def control_device(device: str, state: str) -> bool:
    """Control one supported ESP32 device."""
    url = _endpoint(device, state)

    try:
        response = requests.get(
            url,
            timeout=HTTP_TIMEOUT,
        )
        return response.status_code == 200

    except requests.RequestException as exc:
        print(f"[AUTOMATION] ESP32 request failed: {exc}")
        return False


def get_hardware_status():
    """Return ESP32 /status JSON, or None when unavailable."""
    if not BASE_URL:
        return None

    try:
        response = requests.get(
            f"{BASE_URL}/status",
            timeout=HTTP_TIMEOUT,
        )
        if response.status_code != 200:
            return None
        return response.json()

    except (requests.RequestException, ValueError):
        return None


def home_automation(data=None):
    """
    Registry action.

    Examples:
        {"device": "light", "action": "turn_on"}
        {"device": "fan", "action": "OFF"}
        {"action": "status"}
    """
    data = data if isinstance(data, dict) else {}

    if str(data.get("action", "")).lower() == "status":
        status = get_hardware_status()
        return status if status is not None else {
            "ok": False,
            "error": "ESP32 is unreachable or not configured.",
        }

    device = str(data.get("device", "")).strip().lower()
    action = str(data.get("action", "")).strip().lower()

    if not device:
        return "Please specify a device, such as light or fan."

    if any(word in action for word in ("on", "enable", "start")):
        state = "ON"
    elif any(word in action for word in ("off", "disable", "stop")):
        state = "OFF"
    else:
        return "Please specify ON or OFF."

    ok = control_device(device, state)

    if ok:
        return f"{device} turned {state.lower()}."

    return (
        f"I could not reach the ESP32 to turn the "
        f"{device} {state.lower()}."
    )


register(
    "home_automation",
    home_automation,
    category="automation",
)
