"""
JARVIS PRO
HUD Event Bus

Lightweight event system connecting JARVIS
to the future HUD.

The bus contains no UI logic.
"""

import threading

from .events import HUDEvent


class HUDEventBus:

    def __init__(self):

        self._listeners = []

        self._lock = threading.Lock()

    # =====================================================
    # Subscribe
    # =====================================================

    def subscribe(self, callback):

        if callback is None:
            return

        with self._lock:

            if callback not in self._listeners:

                self._listeners.append(
                    callback
                )

    # =====================================================
    # Unsubscribe
    # =====================================================

    def unsubscribe(self, callback):

        with self._lock:

            if callback in self._listeners:

                self._listeners.remove(
                    callback
                )

    # =====================================================
    # Publish
    # =====================================================

    def publish(self, event: HUDEvent):

        with self._lock:

            listeners = list(
                self._listeners
            )

        for callback in listeners:

            try:

                callback(event)

            except Exception as e:

                print(
                    "[HUD BUS] Listener error:",
                    e
                )


# Global HUD event bus

hud_bus = HUDEventBus()