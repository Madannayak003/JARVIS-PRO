"""
JARVIS PRO HUD
System Panel
"""

from ..widgets import Panel, ProgressBar


class SystemPanel:

    def __init__(
        self,
        canvas,
        state,
    ):

        self.canvas = canvas

        self.state = state

    # --------------------------------------------------

    def draw(
        self,
        x,
        y,
        width,
        height,
    ):

        panel = Panel(

            self.canvas,
            x,
            y,
            width,
            height,
            "SYSTEM"

        )

        panel.draw()

        system = self.state.system

        cpu = system.get("cpu")

        ram = system.get("ram")

        battery = system.get("battery")

        ProgressBar(
            self.canvas,
            x + 18,
            y + 55,
            width - 90,
            cpu,
            "CPU"
        ).draw()

        ProgressBar(
            self.canvas,
            x + 18,
            y + 85,
            width - 90,
            ram,
            "RAM"
        ).draw()

        ProgressBar(
            self.canvas,
            x + 18,
            y + 115,
            width - 90,
            battery,
            "BAT"
        ).draw()