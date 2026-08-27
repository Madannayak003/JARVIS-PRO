"""
JARVIS PRO HUD

ULTRON / MARK XLIX VISUAL RENDERER

This layer only draws the HUD.
It does not execute JARVIS commands.
"""

import math

from . import theme

from .animations import (
    AnimationEngine,
)


class HUDRenderer:

    def __init__(
        self,
        canvas,
        state,
    ):

        self.canvas = canvas

        self.state = state

        self.animation = (
            AnimationEngine()
        )

    # =====================================================
    # Main Render
    # =====================================================

    def render(self):

        self.canvas.delete(
            "all"
        )

        width = self.canvas.winfo_width()

        height = self.canvas.winfo_height()

        if width < 600 or height < 400:

            return

        # ---------------------------------------------
        # Background
        # ---------------------------------------------

        self.draw_background(
            width,
            height
        )

        # ---------------------------------------------
        # Particles
        # ---------------------------------------------

        self.draw_particles(
            width,
            height
        )

        # ---------------------------------------------
        # Header
        # ---------------------------------------------

        self.draw_header(
            width,
            height
        )

        # ---------------------------------------------
        # Main Ultron Core
        # ---------------------------------------------

        self.draw_ultron_core(
            width / 2,
            height / 2
        )

        # ---------------------------------------------
        # Status
        # ---------------------------------------------

        self.draw_status(
            width,
            height
        )

    # =====================================================
    # Background
    # =====================================================

    def draw_background(
        self,
        width,
        height,
    ):

        self.canvas.create_rectangle(

            0,
            0,

            width,
            height,

            fill=theme.BACKGROUND,

            outline="",

        )

        # ---------------------------------------------
        # Technical grid
        # ---------------------------------------------

        spacing = 55

        for x in range(
            0,
            int(width),
            spacing
        ):

            self.canvas.create_line(

                x,
                0,

                x,
                height,

                fill=theme.GRID,

            )

        for y in range(
            0,
            int(height),
            spacing
        ):

            self.canvas.create_line(

                0,
                y,

                width,
                y,

                fill=theme.GRID,

            )

        # ---------------------------------------------
        # Horizontal scan line
        # ---------------------------------------------

        scan = (
            self.animation.scan_position()
        )

        scan_y = (
            scan
            * height
        )

        self.canvas.create_line(

            0,
            scan_y,

            width,
            scan_y,

            fill=theme.ORANGE_DARK,

            width=1,

        )

    # =====================================================
    # Particles
    # =====================================================

    def draw_particles(
        self,
        width,
        height,
    ):

        for particle in (
            self.animation.particles
        ):

            x, y = (
                self.animation
                .particle_position(
                    particle
                )
            )

            px = x * width

            py = y * height

            size = particle["size"]

            self.canvas.create_oval(

                px - size,
                py - size,

                px + size,
                py + size,

                fill=theme.ORANGE_DIM,

                outline="",

            )

    # =====================================================
    # Header
    # =====================================================

    def draw_header(
        self,
        width,
        height,
    ):

        self.canvas.create_text(

            25,
            25,

            text="JARVIS PRO",

            anchor="w",

            fill=theme.ORANGE,

            font=(
                theme.MONO,
                13,
                "bold"
            ),

        )

        self.canvas.create_text(

            width / 2,
            25,

            text="JARVIS",

            anchor="center",

            fill=theme.ORANGE_HOT,

            font=(
                theme.FONT,
                17,
                "bold"
            ),

        )

        self.canvas.create_text(

            width - 25,
            25,

            text=(
                "SYSTEM  "
                + self.state.status.upper()
            ),

            anchor="e",

            fill=theme.HUD_TEXT,

            font=(
                theme.MONO,
                9,
                "bold"
            ),

        )

        self.canvas.create_line(

            20,
            48,

            width - 20,
            48,

            fill=theme.HUD_BORDER,

        )

    # =====================================================
    # ULTRON CORE
    # =====================================================

    def draw_ultron_core(
        self,
        cx,
        cy,
    ):

        pulse = (
            self.animation.pulse(
                2.0
            )
        )

        rotation = (
            self.animation.rotation(
                0.08
            )
        )

        # ---------------------------------------------
        # Core size
        # ---------------------------------------------

        base = 145

        # ---------------------------------------------
        # Outer orbital rings
        # ---------------------------------------------

        rings = (

            260,

            235,

            210,

            185,

            160,

        )

        for i, radius in enumerate(
            rings
        ):

            dynamic = (
                math.sin(
                    self.animation.elapsed()
                    * 0.7
                    + i
                )
                * 3
            )

            r = radius + dynamic

            self.canvas.create_oval(

                cx - r,
                cy - r,

                cx + r,
                cy + r,

                outline=(
                    theme.ORANGE_DIM
                    if i
                    else theme.ORANGE
                ),

                width=1,

            )

        # ---------------------------------------------
        # Rotating orbital segments
        # ---------------------------------------------

        for ring_index, radius in enumerate(
            (
                175,
                205,
                235,
            )
        ):

            for segment in range(12):

                angle = math.radians(

                    rotation
                    + segment * 30
                    + ring_index * 12

                )

                gap = (
                    0.045
                    if segment % 2
                    else 0.018
                )

                start = angle + gap

                end = (
                    angle
                    + math.radians(
                        20
                    )
                    - gap
                )

                self._arc(

                    cx,
                    cy,

                    radius,

                    start,

                    end,

                )

        # ---------------------------------------------
        # Sphere latitude lines
        # ---------------------------------------------

        for i in range(
            -5,
            6
        ):

            y_offset = (
                i
                * 18
            )

            width_factor = math.sqrt(

                max(

                    0,

                    1
                    - (
                        y_offset
                        / 100
                    ) ** 2

                )

            )

            x_radius = (
                base
                * width_factor
            )

            self.canvas.create_arc(

                cx - x_radius,
                cy - 100,

                cx + x_radius,
                cy + 100,

                start=0,

                extent=360,

                style="arc",

                outline=theme.ORANGE_DARK,

            )

        # ---------------------------------------------
        # Sphere longitude lines
        # ---------------------------------------------

        for angle in range(
            0,
            180,
            20
        ):

            radians = math.radians(
                angle
            )

            x_radius = (
                base
                * abs(
                    math.cos(
                        radians
                    )
                )
            )

            self.canvas.create_oval(

                cx - x_radius,
                cy - base,

                cx + x_radius,
                cy + base,

                outline=theme.ORANGE_DARK,

            )

        # ---------------------------------------------
        # Energy glow layers
        # ---------------------------------------------

        glow_sizes = (

            110,
            90,
            70,
            50,

        )

        for i, radius in enumerate(
            glow_sizes
        ):

            dynamic = (
                pulse
                * (
                    8
                    - i
                )
            )

            r = radius + dynamic

            self.canvas.create_oval(

                cx - r,
                cy - r,

                cx + r,
                cy + r,

                fill=(
                    theme.ORANGE_DARK
                    if i == 0
                    else theme.BACKGROUND_SOFT
                ),

                outline=(
                    theme.ORANGE_DIM
                    if i < 2
                    else theme.ORANGE
                ),

                width=1,

            )

        # ---------------------------------------------
        # Central energy
        # ---------------------------------------------

        core_radius = (
            25
            + pulse * 8
        )

        self.canvas.create_oval(

            cx - core_radius,
            cy - core_radius,

            cx + core_radius,
            cy + core_radius,

            fill=theme.ORANGE,

            outline=theme.ORANGE_HOT,

            width=2,

        )

        # ---------------------------------------------
        # Energy cross
        # ---------------------------------------------

        cross = (
            core_radius
            + 20
        )

        self.canvas.create_line(

            cx - cross,
            cy,

            cx + cross,
            cy,

            fill=theme.ORANGE_DIM,

        )

        self.canvas.create_line(

            cx,
            cy - cross,

            cx,
            cy + cross,

            fill=theme.ORANGE_DIM,

        )

        # ---------------------------------------------
        # Center
        # ---------------------------------------------

        self.canvas.create_oval(

            cx - 8,
            cy - 8,

            cx + 8,
            cy + 8,

            fill=theme.ORANGE_HOT,

            outline="",

        )

        self.canvas.create_text(

            cx,
            cy + 300,

            text="JARVIS",

            fill=theme.ORANGE,

            font=(
                theme.MONO,
                12,
                "bold"
            ),

        )

    # =====================================================
    # Arc Helper
    # =====================================================

    def _arc(
        self,
        cx,
        cy,
        radius,
        start,
        end,
    ):

        start_deg = math.degrees(
            start
        )

        extent_deg = math.degrees(
            end - start
        )

        self.canvas.create_arc(

            cx - radius,
            cy - radius,

            cx + radius,
            cy + radius,

            start=start_deg,

            extent=extent_deg,

            style="arc",

            outline=theme.ORANGE,

            width=1,

        )

    # =====================================================
    # Status
    # =====================================================

    def draw_status(
        self,
        width,
        height,
    ):

        if self.state.listening:

            label = "LISTENING"

        elif self.state.thinking:

            label = "THINKING"

        elif self.state.speaking:

            label = "SPEAKING"

        elif self.state.executing:

            label = "EXECUTING"

        else:

            label = "STANDBY"

        self.canvas.create_text(

            width / 2,

            height - 55,

            text=label,

            fill=theme.ORANGE_HOT,

            font=(
                theme.MONO,
                11,
                "bold"
            ),

        )

        self.canvas.create_text(

            width / 2,

            height - 30,

            text=(
                "ULTRON CORE  //  "
                "JARVIS PRO"
            ),

            fill=theme.HUD_DIM,

            font=(
                theme.MONO,
                8
            ),

        )