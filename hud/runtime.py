"""
JARVIS PRO
HUD Runtime

Owns the HUD runtime lifecycle.

IMPORTANT:
This module does not control JARVIS.
It only provides the HUD side of the runtime.

Communication transport will be added separately.
"""

import threading


class HUDRuntime:

    def __init__(self):

        self.running = False
        self.thread = None

    # =====================================================
    # Start
    # =====================================================

    def start(self):

        if self.running:

            return

        self.running = True

        print(
            "[HUD RUNTIME] Started."
        )

    # =====================================================
    # Stop
    # =====================================================

    def stop(self):

        if not self.running:

            return

        self.running = False

        print(
            "[HUD RUNTIME] Stopped."
        )

    # =====================================================
    # Status
    # =====================================================

    def is_running(self):

        return self.running


# =========================================================
# Singleton
# =========================================================

hud_runtime = HUDRuntime()