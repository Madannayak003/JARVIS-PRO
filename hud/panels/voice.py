"""
JARVIS PRO HUD
Voice Panel
"""

from .. import theme
from ..widgets import Panel


class VoicePanel:

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
            "VOICE"

        )

        panel.draw()

        if self.state.listening:

            status = "LISTENING"

        elif self.state.speaking:

            status = "SPEAKING"

        elif self.state.thinking:

            status = "THINKING"

        elif self.state.executing:

            status = "EXECUTING"

        else:

            status = "STANDBY"

        self.canvas.create_text(

            x + 18,
            y + 60,

            text=status,

            anchor="w",

            fill=theme.CYAN,

            font=(
                theme.MONO,
                13,
                "bold"
            ),

        )

        self.canvas.create_text(

            x + 18,
            y + 88,

            text=(
                f"MODE  {self.state.voice_mode.upper()}"
            ),

            anchor="w",

            fill=theme.TEXT,

            font=(
                theme.MONO,
                9
            ),

        )