"""
JARVIS PRO HUD
Main Application
"""

import queue
import tkinter as tk

from .bus import hud_bus

from .events import (
    HUDEvent,
    HUD_COMMAND,
    HUD_RESPONSE,
    HUD_SYSTEM_UPDATE,
)

from .manager import hud

from .telemetry import telemetry

from .renderer import HUDRenderer

from . import theme


class HUDApplication:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title(
            "JARVIS PRO"
        )

        self.root.geometry(
            "1400x850"
        )

        self.root.minsize(
            1000,
            650
        )

        self.root.configure(
            bg=theme.BACKGROUND
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.canvas = tk.Canvas(

            self.root,

            bg=theme.BACKGROUND,

            highlightthickness=0,

        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self.renderer = HUDRenderer(

            self.canvas,

            hud.state

        )

        self.event_queue = queue.Queue()

        hud_bus.subscribe(
            self._receive_event
        )

        self.running = True

        self._schedule_render()

        self._schedule_telemetry()

    # =====================================================
    # Event Bridge
    # =====================================================

    def _receive_event(
        self,
        event: HUDEvent,
    ):

        self.event_queue.put(
            event
        )

    # =====================================================
    # Process Events
    # =====================================================

    def _process_events(self):

        while True:

            try:

                event = (
                    self.event_queue.get_nowait()
                )

            except queue.Empty:

                break

            self._handle_event(
                event
            )

    # -----------------------------------------------------

    def _handle_event(
        self,
        event,
    ):

        if event.name == HUD_COMMAND:

            hud.state.last_command = (
                event.data.get(
                    "text",
                    ""
                )
            )

        elif event.name == HUD_RESPONSE:

            hud.state.last_response = (
                event.data.get(
                    "text",
                    ""
                )
            )

    # =====================================================
    # Render Loop
    # =====================================================

    def _schedule_render(self):

        if not self.running:
            return

        self._process_events()

        self.renderer.render()

        self.root.after(
            33,
            self._schedule_render
        )

    # =====================================================
    # Telemetry
    # =====================================================

    def _schedule_telemetry(self):

        if not self.running:
            return

        data = telemetry.read()

        hud.system_update(
            data
        )

        self.root.after(
            1000,
            self._schedule_telemetry
        )

    # =====================================================
    # Start
    # =====================================================

    def run(self):

        hud.idle()

        self.root.mainloop()

    # =====================================================
    # Close
    # =====================================================

    def close(self):

        self.running = False

        hud_bus.unsubscribe(
            self._receive_event
        )

        self.root.destroy()


def start_hud():

    application = HUDApplication()

    application.run()


if __name__ == "__main__":

    start_hud()