"""
JARVIS PRO
HUD Visual Interface

Simple HUD Foundation.

IMPORTANT:
This UI is READ-ONLY.

It does NOT:
- execute commands
- control voice
- control AI
- control Developer Mode
- modify JARVIS runtime
- send commands to JARVIS

It only reads:
    HUDManager state
    HUD Telemetry
"""

import math
import tkinter as tk

from .manager import hud
from .telemetry import telemetry


# ============================================================
# COLORS
# ============================================================

BG = "#05080D"
PANEL = "#0B1118"
PANEL_ALT = "#0E151E"

TEXT = "#E8F1F8"
TEXT_DIM = "#71808E"

BORDER = "#1B2A38"

ACCENT = "#00D9FF"
ACCENT_DIM = "#087D92"

SUCCESS = "#00FF9C"
WARNING = "#FFD166"
ERROR = "#FF4D6D"


# ============================================================
# HUD WINDOW
# ============================================================

class HUDWindow:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title(
            "JARVIS PRO HUD"
        )

        self.root.geometry(
            "1100x700"
        )

        self.root.minsize(
            900,
            600
        )

        self.root.configure(
            bg=BG
        )

        self.running = True

        # Animation
        self.animation_phase = 0

        # Build interface
        self._build_ui()

        # Start UI update loop
        self._update_loop()

        # Start status animation
        self._animate_status()

        # Window close handler
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def _frame(
        self,
        parent,
        **kwargs
    ):

        return tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            highlightthickness=1,
            bd=0,
            **kwargs
        )

    def _label(
        self,
        parent,
        text="",
        size=11,
        bold=False,
        color=TEXT,
        **kwargs
    ):

        return tk.Label(
            parent,
            text=text,
            bg=PANEL,
            fg=color,
            font=(
                "Segoe UI",
                size,
                "bold" if bold else "normal"
            ),
            **kwargs
        )

    # ========================================================
    # BUILD UI
    # ========================================================

    def _build_ui(self):

        # ====================================================
        # ROOT
        # ====================================================

        self.main = tk.Frame(
            self.root,
            bg=BG
        )

        self.main.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=18
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = tk.Frame(
            self.main,
            bg=BG
        )

        header.pack(
            fill="x",
            pady=(0, 14)
        )

        # ----------------------------------------------------
        # Header left
        # ----------------------------------------------------

        header_left = tk.Frame(
            header,
            bg=BG
        )

        header_left.pack(
            side="left",
            anchor="w"
        )

        self.title_label = tk.Label(
            header_left,
            text="JARVIS PRO",
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                27,
                "bold"
            )
        )

        self.title_label.pack(
            anchor="w"
        )

        self.subtitle_label = tk.Label(
            header_left,
            text="ARTIFICIAL INTELLIGENCE  •  SYSTEM HUD",
            bg=BG,
            fg=ACCENT,
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        )

        self.subtitle_label.pack(
            anchor="w",
            pady=(1, 0)
        )

        # ----------------------------------------------------
        # Header right
        # ----------------------------------------------------

        header_right = tk.Frame(
            header,
            bg=BG
        )

        header_right.pack(
            side="right",
            anchor="e",
            pady=5
        )

        self.header_status_dot = tk.Label(
            header_right,
            text="●",
            bg=BG,
            fg=SUCCESS,
            font=(
                "Segoe UI",
                12,
                "bold"
            )
        )

        self.header_status_dot.pack(
            side="left",
            padx=(0, 5)
        )

        self.header_status = tk.Label(
            header_right,
            text="STANDALONE",
            bg=BG,
            fg=TEXT_DIM,
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        )

        self.header_status.pack(
            side="left"
        )

        # ====================================================
        # MAIN STATUS
        # ====================================================

        status_frame = self._frame(
            self.main
        )

        status_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        status_header = self._label(
            status_frame,
            text="SYSTEM STATUS",
            size=9,
            bold=True,
            color=TEXT_DIM
        )

        status_header.pack(
            anchor="w",
            padx=18,
            pady=(11, 0)
        )

        self.status_canvas = tk.Canvas(
            status_frame,
            height=105,
            bg=PANEL,
            highlightthickness=0,
            bd=0
        )

        self.status_canvas.pack(
            fill="x",
            padx=18
        )

        self.status_label = self._label(
            status_frame,
            text="IDLE",
            size=26,
            bold=True,
            color=TEXT
        )

        self.status_label.place(
            relx=0.5,
            rely=0.55,
            anchor="center"
        )

        # ====================================================
        # CORE INFORMATION
        # ====================================================

        core_row = tk.Frame(
            self.main,
            bg=BG
        )

        core_row.pack(
            fill="x",
            pady=(0, 12)
        )

        # ====================================================
        # VOICE
        # ====================================================

        voice_frame = self._frame(
            core_row
        )

        voice_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        self._label(
            voice_frame,
            text="VOICE CORE",
            size=9,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=16,
            pady=(11, 3)
        )

        self.voice_label = self._label(
            voice_frame,
            text="ONLINE",
            size=17,
            bold=True,
            color=SUCCESS
        )

        self.voice_label.pack(
            anchor="w",
            padx=16,
            pady=(0, 11)
        )

        # ====================================================
        # AI
        # ====================================================

        ai_frame = self._frame(
            core_row
        )

        ai_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        self._label(
            ai_frame,
            text="AI CORE",
            size=9,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=16,
            pady=(11, 3)
        )

        self.ai_label = self._label(
            ai_frame,
            text="UNKNOWN",
            size=15,
            bold=True,
            color=ACCENT
        )

        self.ai_label.pack(
            anchor="w",
            padx=16,
            pady=(0, 11)
        )

        # ====================================================
        # TASK
        # ====================================================

        task_frame = self._frame(
            core_row
        )

        task_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 0)
        )

        self._label(
            task_frame,
            text="ACTIVE TASK",
            size=9,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=16,
            pady=(11, 3)
        )

        self.task_label = self._label(
            task_frame,
            text="NONE",
            size=14,
            bold=True,
            color=TEXT
        )

        self.task_label.pack(
            anchor="w",
            padx=16,
            pady=(0, 11)
        )

        # ====================================================
        # TELEMETRY
        # ====================================================

        telemetry_frame = self._frame(
            self.main
        )

        telemetry_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        self._label(
            telemetry_frame,
            text="SYSTEM TELEMETRY",
            size=9,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=18,
            pady=(11, 7)
        )

        telemetry_row = tk.Frame(
            telemetry_frame,
            bg=PANEL
        )

        telemetry_row.pack(
            fill="x",
            padx=16,
            pady=(0, 13)
        )

        # ====================================================
        # CPU
        # ====================================================

        cpu_box = tk.Frame(
            telemetry_row,
            bg=PANEL_ALT
        )

        cpu_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        self._label(
            cpu_box,
            text="CPU",
            size=8,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=12,
            pady=(8, 0)
        )

        self.cpu_label = self._label(
            cpu_box,
            text="--%",
            size=15,
            bold=True,
            color=ACCENT
        )

        self.cpu_label.pack(
            anchor="w",
            padx=12,
            pady=(0, 3)
        )

        self.cpu_bar = tk.Canvas(
            cpu_box,
            height=5,
            bg=PANEL_ALT,
            highlightthickness=0
        )

        self.cpu_bar.pack(
            fill="x",
            padx=12,
            pady=(0, 9)
        )

        # ====================================================
        # RAM
        # ====================================================

        ram_box = tk.Frame(
            telemetry_row,
            bg=PANEL_ALT
        )

        ram_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        self._label(
            ram_box,
            text="RAM",
            size=8,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=12,
            pady=(8, 0)
        )

        self.ram_label = self._label(
            ram_box,
            text="--%",
            size=15,
            bold=True,
            color=ACCENT
        )

        self.ram_label.pack(
            anchor="w",
            padx=12,
            pady=(0, 3)
        )

        self.ram_bar = tk.Canvas(
            ram_box,
            height=5,
            bg=PANEL_ALT,
            highlightthickness=0
        )

        self.ram_bar.pack(
            fill="x",
            padx=12,
            pady=(0, 9)
        )

        # ====================================================
        # BATTERY
        # ====================================================

        battery_box = tk.Frame(
            telemetry_row,
            bg=PANEL_ALT
        )

        battery_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 0)
        )

        self._label(
            battery_box,
            text="BATTERY",
            size=8,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=12,
            pady=(8, 0)
        )

        self.battery_label = self._label(
            battery_box,
            text="--%",
            size=15,
            bold=True,
            color=SUCCESS
        )

        self.battery_label.pack(
            anchor="w",
            padx=12,
            pady=(0, 3)
        )

        self.battery_bar = tk.Canvas(
            battery_box,
            height=5,
            bg=PANEL_ALT,
            highlightthickness=0
        )

        self.battery_bar.pack(
            fill="x",
            padx=12,
            pady=(0, 9)
        )

        # ====================================================
        # BOTTOM INFORMATION
        # ====================================================

        bottom_row = tk.Frame(
            self.main,
            bg=BG
        )

        bottom_row.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # NOTIFICATION
        # ====================================================

        notification_frame = self._frame(
            bottom_row
        )

        notification_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        self._label(
            notification_frame,
            text="NOTIFICATION",
            size=9,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=16,
            pady=(11, 5)
        )

        self.notification_label = self._label(
            notification_frame,
            text="No notifications.",
            size=10,
            color=TEXT
        )

        self.notification_label.pack(
            anchor="w",
            padx=16,
            pady=(0, 12)
        )

        # ====================================================
        # SYSTEM MESSAGE
        # ====================================================

        error_frame = self._frame(
            bottom_row
        )

        error_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 0)
        )

        self._label(
            error_frame,
            text="SYSTEM MESSAGE",
            size=9,
            bold=True,
            color=TEXT_DIM
        ).pack(
            anchor="w",
            padx=16,
            pady=(11, 5)
        )

        self.error_label = self._label(
            error_frame,
            text="System operational.",
            size=10,
            color=SUCCESS
        )

        self.error_label.pack(
            anchor="w",
            padx=16,
            pady=(0, 12)
        )

        # ====================================================
        # FOOTER
        # ====================================================

        self.footer = tk.Label(
            self.main,
            text="JARVIS PRO  •  HUD FOUNDATION  •  STANDALONE",
            bg=BG,
            fg=TEXT_DIM,
            font=(
                "Segoe UI",
                8
            )
        )

        self.footer.pack(
            anchor="e",
            pady=(8, 0)
        )

    # ========================================================
    # DRAW TELEMETRY BAR
    # ========================================================

    def _draw_bar(
        self,
        canvas,
        value,
        maximum=100
    ):

        canvas.delete("all")

        try:

            # Ignore unavailable values
            if value is None:
                return

            if isinstance(value, str):

                if value.strip() in (
                    "",
                    "--",
                    "None"
                ):
                    return

            value = float(value)

            value = max(
                0,
                min(
                    value,
                    maximum
                )
            )

            width = canvas.winfo_width()

            if width <= 1:
                return

            height = 5

            # ------------------------------------------------
            # Background
            # ------------------------------------------------

            canvas.create_rectangle(
                0,
                0,
                width,
                height,
                fill=BORDER,
                outline=""
            )

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            progress = (
                value / maximum
            )

            canvas.create_rectangle(
                0,
                0,
                width * progress,
                height,
                fill=ACCENT,
                outline=""
            )

        except (
            ValueError,
            TypeError
        ):

            # Never allow telemetry values to
            # break the HUD UI.
            return

    # ========================================================
    # BATTERY VISUAL
    # ========================================================

    def _update_battery_visual(
        self,
        battery
    ):

        if battery is None:

            self.battery_label.config(
                text="--%",
                fg=TEXT_DIM
            )

            return

        try:

            battery = float(
                battery
            )

        except (
            ValueError,
            TypeError
        ):

            self.battery_label.config(
                text="--%",
                fg=TEXT_DIM
            )

            return

        if battery <= 15:

            color = ERROR

        elif battery <= 30:

            color = WARNING

        else:

            color = SUCCESS

        self.battery_label.config(
            text=f"{battery:.0f}%",
            fg=color
        )

    # ========================================================
    # READ HUD STATE
    # ========================================================

    def _read_state(self):

        state = hud.state

        return {
            "status": state.status,
            "voice_mode": state.voice_mode,
            "ai_model": state.ai_model,
            "current_task": state.current_task,
            "task_status": state.task_status,
            "system": state.system,
            "notification": state.notification,
            "error": state.error,
        }

    # ========================================================
    # STATUS COLOR
    # ========================================================

    def _status_color(
        self,
        status
    ):

        status = str(
            status
        ).lower()

        if status == "listening":

            return ACCENT

        if status == "thinking":

            return WARNING

        if status == "speaking":

            return SUCCESS

        if status == "executing":

            return ACCENT

        if status == "error":

            return ERROR

        if status == "idle":

            return TEXT

        return TEXT

    # ========================================================
    # STATUS ANIMATION
    # ========================================================

    def _animate_status(self):

        if not self.running:
            return

        try:

            state = hud.state

            status = str(
                state.status
            ).lower()

            self.status_canvas.delete(
                "animation"
            )

            width = self.status_canvas.winfo_width()

            if width <= 1:

                width = 800

            center_x = width / 2
            center_y = 58

            self.animation_phase += 1

            phase = self.animation_phase

            # =================================================
            # IDLE
            # =================================================

            if status == "idle":

                radius = 4

                self.status_canvas.create_oval(
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                    fill=TEXT_DIM,
                    outline="",
                    tags="animation"
                )

            # =================================================
            # LISTENING
            # =================================================

            elif status == "listening":

                pulse = phase % 30

                if pulse > 15:

                    pulse = 30 - pulse

                radius = 12 + (
                    pulse * 1.5
                )

                self.status_canvas.create_oval(
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                    outline=ACCENT,
                    width=2,
                    tags="animation"
                )

                inner = 5

                self.status_canvas.create_oval(
                    center_x - inner,
                    center_y - inner,
                    center_x + inner,
                    center_y + inner,
                    fill=ACCENT,
                    outline="",
                    tags="animation"
                )

            # =================================================
            # THINKING
            # =================================================

            elif status == "thinking":

                dot_count = 5
                spacing = 18

                start_x = (
                    center_x
                    - (
                        (dot_count - 1)
                        * spacing
                        / 2
                    )
                )

                active = (
                    phase // 8
                ) % dot_count

                for i in range(dot_count):

                    radius = 4

                    if i == active:

                        radius = 7

                    x = (
                        start_x
                        + i * spacing
                    )

                    self.status_canvas.create_oval(
                        x - radius,
                        center_y - radius,
                        x + radius,
                        center_y + radius,
                        fill=WARNING,
                        outline="",
                        tags="animation"
                    )

            # =================================================
            # SPEAKING
            # =================================================

            elif status == "speaking":

                bars = 9
                spacing = 14

                start_x = (
                    center_x
                    - (
                        (bars - 1)
                        * spacing
                        / 2
                    )
                )

                for i in range(bars):

                    wave = (
                        phase * 0.35
                        + i * 0.9
                    )

                    height = (
                        10
                        + abs(
                            math.sin(wave)
                        ) * 28
                    )

                    x = (
                        start_x
                        + i * spacing
                    )

                    self.status_canvas.create_rectangle(
                        x - 3,
                        center_y - height / 2,
                        x + 3,
                        center_y + height / 2,
                        fill=SUCCESS,
                        outline="",
                        tags="animation"
                    )

            # =================================================
            # EXECUTING
            # =================================================

            elif status == "executing":

                radius = 28

                rotation = (
                    phase * 8
                )

                for i in range(8):

                    angle = math.radians(
                        rotation
                        + i * 45
                    )

                    x = (
                        center_x
                        + math.cos(angle)
                        * radius
                    )

                    y = (
                        center_y
                        + math.sin(angle)
                        * radius
                    )

                    dot_radius = 3

                    self.status_canvas.create_oval(
                        x - dot_radius,
                        y - dot_radius,
                        x + dot_radius,
                        y + dot_radius,
                        fill=ACCENT,
                        outline="",
                        tags="animation"
                    )

            # =================================================
            # ERROR
            # =================================================

            elif status == "error":

                pulse = phase % 20

                radius = (
                    12
                    + pulse * 0.7
                )

                self.status_canvas.create_oval(
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                    outline=ERROR,
                    width=3,
                    tags="animation"
                )

                self.status_canvas.create_oval(
                    center_x - 5,
                    center_y - 5,
                    center_x + 5,
                    center_y + 5,
                    fill=ERROR,
                    outline="",
                    tags="animation"
                )

            # =================================================
            # NEXT ANIMATION FRAME
            # =================================================

            self.root.after(
                50,
                self._animate_status
            )

        except Exception as e:

            print(
                "[HUD ANIMATION ERROR]",
                e
            )

            try:

                self.root.after(
                    100,
                    self._animate_status
                )

            except Exception:
                pass

    # ========================================================
    # UPDATE TELEMETRY
    # ========================================================

    def _update_telemetry(self):

        try:

            data = telemetry.read()

            cpu = data.get(
                "cpu"
            )

            ram = data.get(
                "ram"
            )

            battery = data.get(
                "battery"
            )

            # ------------------------------------------------
            # CPU
            # ------------------------------------------------

            if cpu is None:

                self.cpu_label.config(
                    text="--%"
                )

            else:

                try:

                    cpu = float(cpu)

                    self.cpu_label.config(
                        text=f"{cpu:.1f}%"
                    )

                    self._draw_bar(
                        self.cpu_bar,
                        cpu
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    self.cpu_label.config(
                        text="--%"
                    )

            # ------------------------------------------------
            # RAM
            # ------------------------------------------------

            if ram is None:

                self.ram_label.config(
                    text="--%"
                )

            else:

                try:

                    ram = float(ram)

                    self.ram_label.config(
                        text=f"{ram:.1f}%"
                    )

                    self._draw_bar(
                        self.ram_bar,
                        ram
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    self.ram_label.config(
                        text="--%"
                    )

            # ------------------------------------------------
            # BATTERY
            # ------------------------------------------------

            self._update_battery_visual(
                battery
            )

            if battery is not None:

                try:

                    battery = float(
                        battery
                    )

                    self._draw_bar(
                        self.battery_bar,
                        battery
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    pass

        except Exception as e:

            print(
                "[HUD TELEMETRY ERROR]",
                e
            )

    # ========================================================
    # UPDATE UI
    # ========================================================

    def _update_loop(self):

        if not self.running:

            return

        try:

            state = self._read_state()

            # =================================================
            # STATUS
            # =================================================

            status = state[
                "status"
            ]

            status_text = str(
                status
            ).upper()

            self.status_label.config(
                text=status_text,
                fg=self._status_color(
                    status
                )
            )

            # ------------------------------------------------
            # Header status
            # ------------------------------------------------

            if str(status).lower() == "error":

                self.header_status_dot.config(
                    fg=ERROR
                )

                self.header_status.config(
                    text="SYSTEM ERROR",
                    fg=ERROR
                )

            else:

                self.header_status_dot.config(
                    fg=SUCCESS
                )

                self.header_status.config(
                    text="STANDALONE",
                    fg=TEXT_DIM
                )

            # =================================================
            # VOICE MODE
            # =================================================

            voice_mode = str(
                state["voice_mode"]
            ).upper()

            self.voice_label.config(
                text=voice_mode,
                fg=(
                    SUCCESS
                    if voice_mode == "ONLINE"
                    else ACCENT
                )
            )

            # =================================================
            # AI MODEL
            # =================================================

            ai_model = state[
                "ai_model"
            ]

            if not ai_model:

                ai_model = "UNKNOWN"

            self.ai_label.config(
                text=str(
                    ai_model
                ).upper()
            )

            # =================================================
            # TASK
            # =================================================

            task = state[
                "current_task"
            ]

            if not task:

                task = "NONE"

            task_status = state[
                "task_status"
            ]

            if not task_status:

                task_status = ""

            if task_status:

                task_text = (
                    f"{task} "
                    f"[{task_status}]"
                )

            else:

                task_text = str(
                    task
                )

            self.task_label.config(
                text=task_text
            )

            # =================================================
            # TELEMETRY
            # =================================================

            self._update_telemetry()

            # =================================================
            # NOTIFICATION
            # =================================================

            notification = (
                state["notification"]
                or "No notifications."
            )

            self.notification_label.config(
                text=str(
                    notification
                )
            )

            # =================================================
            # SYSTEM MESSAGE
            # =================================================

            error = state[
                "error"
            ]

            if error:

                self.error_label.config(
                    text=str(
                        error
                    ),
                    fg=ERROR
                )

            else:

                self.error_label.config(
                    text="System operational.",
                    fg=SUCCESS
                )

        except Exception as e:

            print(
                "[HUD UI ERROR]",
                e
            )

        # ====================================================
        # NEXT UI UPDATE
        #
        # 1 second is enough for the foundation.
        # Status animation runs independently at 50ms.
        # ====================================================

        try:

            self.root.after(
                1000,
                self._update_loop
            )

        except Exception:

            pass

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        print(
            "[HUD UI] Starting HUD window..."
        )

        self.root.mainloop()

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        self.running = False

        try:

            self.root.destroy()

        except Exception:

            pass


# ============================================================
# START HUD
# ============================================================

def start_hud():

    window = HUDWindow()

    window.run()


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    start_hud()