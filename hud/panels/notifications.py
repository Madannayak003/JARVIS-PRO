"""
JARVIS PRO HUD
Notification Panel
"""

from .. import theme
from ..widgets import Panel


class NotificationPanel:

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
            "STATUS"

        )

        panel.draw()

        message = (
            self.state.notification
            or self.state.error
            or "JARVIS SYSTEM READY"
        )

        self.canvas.create_text(

            x + 18,
            y + 60,

            text=message[:55],

            anchor="w",

            fill=(
                theme.RED
                if self.state.error
                else theme.TEXT
            ),

            font=(
                theme.MONO,
                9
            ),

        )