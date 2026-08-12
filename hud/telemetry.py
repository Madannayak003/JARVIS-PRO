"""
JARVIS PRO
HUD Telemetry Engine

Provides standalone system telemetry for the HUD.

IMPORTANT:
This module does NOT:
- control JARVIS
- execute commands
- access voice
- access AI
- access Developer Mode

It only reads:
- CPU usage
- RAM usage
- Battery percentage
"""

import time

try:
    import psutil
except ImportError:
    psutil = None


class HUDTelemetry:

    def __init__(self):
        self.running = False

    # =====================================================
    # CPU
    # =====================================================

    def get_cpu(self):

        if psutil is None:
            return None

        try:
            return round(
                psutil.cpu_percent(
                    interval=None
                ),
                1
            )

        except Exception:
            return None

    # =====================================================
    # RAM
    # =====================================================

    def get_ram(self):

        if psutil is None:
            return None

        try:

            memory = psutil.virtual_memory()

            return round(
                memory.percent,
                1
            )

        except Exception:
            return None

    # =====================================================
    # Battery
    # =====================================================

    def get_battery(self):

        if psutil is None:
            return None

        try:

            battery = psutil.sensors_battery()

            if battery is None:
                return None

            return round(
                battery.percent,
                1
            )

        except Exception:
            return None

    # =====================================================
    # All Telemetry
    # =====================================================

    def read(self):

        return {
            "cpu": self.get_cpu(),
            "ram": self.get_ram(),
            "battery": self.get_battery(),
            "timestamp": time.time()
        }

    # =====================================================
    # Availability
    # =====================================================

    def available(self):

        return psutil is not None


# =========================================================
# Singleton
# =========================================================

telemetry = HUDTelemetry()