"""
JARVIS PRO HUD
Activity Panel
"""

from .. import theme
from ..widgets import Panel


class ActivityPanel:

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
            "ACTIVITY"

        )

        panel.draw()

        command = (
            self.state.last_command
            or "No command"
        )

        response = (
            self.state.last_response
            or "Waiting..."
        )

        self.canvas.create_text(

            x + 18,
            y + 58,

            text="COMMAND",

            anchor="w",

            fill=theme.TEXT_DIM,

            font=(
                theme.MONO,
                8
            ),

        )

        self.canvas.create_text(

            x + 18,
            y + 78,

            text=command[:45],

            anchor="w",

            fill=theme.WHITE,

            font=(
                theme.MONO,
                9
            ),

        )

        self.canvas.create_text(

            x + 18,
            y + 112,

            text="RESPONSE",

            anchor="w",

            fill=theme.TEXT_DIM,

            font=(
                theme.MONO,
                8
            ),

        )

        self.canvas.create_text(

            x + 18,
            y + 132,

            text=response[:45],

            anchor="w",

            fill=theme.WHITE,

            font=(
                theme.MONO,
                9
            ),

        )