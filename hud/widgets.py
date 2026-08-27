"""
JARVIS PRO HUD
Reusable Visual Widgets
"""

import tkinter as tk

from . import theme


class Panel:

    def __init__(
        self,
        canvas,
        x,
        y,
        width,
        height,
        title="",
    ):

        self.canvas = canvas

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.title = title

    # --------------------------------------------------

    def draw(self):

        self.canvas.create_rectangle(

            self.x,
            self.y,

            self.x + self.width,
            self.y + self.height,

            fill=theme.PANEL_DARK,

            outline=theme.BORDER,

            width=1,

        )

        if self.title:

            self.canvas.create_text(

                self.x + 18,
                self.y + 18,

                text=self.title.upper(),

                anchor="w",

                fill=theme.CYAN,

                font=(
                    theme.MONO,
                    9,
                    "bold"
                ),

            )


class ProgressBar:

    def __init__(
        self,
        canvas,
        x,
        y,
        width,
        value,
        label,
    ):

        self.canvas = canvas

        self.x = x
        self.y = y

        self.width = width

        self.value = value

        self.label = label

    # --------------------------------------------------

    def draw(self):

        self.canvas.create_text(

            self.x,
            self.y,

            text=self.label,

            anchor="w",

            fill=theme.TEXT,

            font=(
                theme.MONO,
                9
            ),

        )

        bar_x = self.x + 55

        self.canvas.create_rectangle(

            bar_x,
            self.y - 5,

            bar_x + self.width,
            self.y + 5,

            fill=theme.PANEL,

            outline=theme.BORDER,

        )

        if self.value is not None:

            fill_width = (
                self.width
                * max(
                    0,
                    min(
                        100,
                        self.value
                    )
                )
                / 100
            )

            self.canvas.create_rectangle(

                bar_x,
                self.y - 5,

                bar_x + fill_width,
                self.y + 5,

                fill=theme.CYAN,

                outline="",

            )