"""
JARVIS PRO
HUD Manager

Central interface for sending information
from JARVIS to the HUD.

The manager does NOT create the visual HUD.
"""

from datetime import datetime

from .bus import hud_bus

from .events import (
    HUDEvent,
    HUD_IDLE,
    HUD_LISTENING,
    HUD_THINKING,
    HUD_SPEAKING,
    HUD_EXECUTING,
    HUD_TASK_STARTED,
    HUD_TASK_FINISHED,
    HUD_TASK_FAILED,
    HUD_VOICE_MODE_CHANGED,
    HUD_AI_MODEL_CHANGED,
    HUD_SYSTEM_UPDATE,
    HUD_NOTIFICATION,
    HUD_ERROR,
)

from .state import HUDState


class HUDManager:

    def __init__(self):

        self.state = HUDState()

    # =====================================================
    # Internal
    # =====================================================

    def _publish(
        self,
        name,
        data=None,
        source=None,
    ):

        if data is None:

            data = {}

        event = HUDEvent(
            name=name,
            data=data,
            source=source,
        )

        self.state.last_event = name

        self.state.last_update = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

        hud_bus.publish(event)

    # =====================================================
    # Status
    # =====================================================

    def set_status(self, status):

        self.state.status = status

        self._publish(
            status,
            {
                "status": status
            },
            source="hud_manager",
        )

    # =====================================================
    # Listening
    # =====================================================

    def listening(self):

        self.state.status = HUD_LISTENING

        self.state.listening = True
        self.state.speaking = False
        self.state.thinking = False
        self.state.executing = False

        self._publish(
            HUD_LISTENING
        )

    # =====================================================
    # Thinking
    # =====================================================

    def thinking(self):

        self.state.status = HUD_THINKING

        self.state.listening = False
        self.state.speaking = False
        self.state.thinking = True
        self.state.executing = False

        self._publish(
            HUD_THINKING
        )

    # =====================================================
    # Speaking
    # =====================================================

    def speaking(self):

        self.state.status = HUD_SPEAKING

        self.state.listening = False
        self.state.speaking = True
        self.state.thinking = False
        self.state.executing = False

        self._publish(
            HUD_SPEAKING
        )

    # =====================================================
    # Executing
    # =====================================================

    def executing(self, task=""):

        self.state.status = HUD_EXECUTING

        self.state.current_task = task
        self.state.task_status = "running"

        self.state.listening = False
        self.state.speaking = False
        self.state.thinking = False
        self.state.executing = True

        self._publish(
            HUD_EXECUTING,
            {
                "task": task
            }
        )

    # =====================================================
    # Task Started
    # =====================================================

    def task_started(self, task):

        self.state.current_task = task
        self.state.task_status = "running"

        self._publish(
            HUD_TASK_STARTED,
            {
                "task": task
            }
        )

    # =====================================================
    # Task Finished
    # =====================================================

    def task_finished(self, task=""):

        self.state.task_status = "finished"
        self.state.executing = False

        self._publish(
            HUD_TASK_FINISHED,
            {
                "task": task
            }
        )

    # =====================================================
    # Task Failed
    # =====================================================

    def task_failed(
        self,
        task="",
        error="",
    ):

        self.state.task_status = "failed"
        self.state.executing = False
        self.state.error = error

        self._publish(
            HUD_TASK_FAILED,
            {
                "task": task,
                "error": error,
            }
        )

    # =====================================================
    # Voice Mode
    # =====================================================

    def voice_mode(self, mode):

        self.state.voice_mode = mode

        self._publish(
            HUD_VOICE_MODE_CHANGED,
            {
                "mode": mode
            }
        )

    # =====================================================
    # AI Model
    # =====================================================

    def ai_model(self, provider, model):

        self.state.ai_model = (
            f"{provider} {model}"
        )

        self._publish(
            HUD_AI_MODEL_CHANGED,
            {
                "provider": provider,
                "model": model,
            }
        )

    # =====================================================
    # System
    # =====================================================

    def system_update(self, data):

        if not isinstance(data, dict):

            return

        self.state.system.update(
            data
        )

        self._publish(
            HUD_SYSTEM_UPDATE,
            data,
        )

    # =====================================================
    # Notification
    # =====================================================

    def notify(self, message):

        self.state.notification = (
            str(message)
        )

        self._publish(
            HUD_NOTIFICATION,
            {
                "message": str(message)
            }
        )

    # =====================================================
    # Error
    # =====================================================

    def error(self, message):

        self.state.error = (
            str(message)
        )

        self._publish(
            HUD_ERROR,
            {
                "error": str(message)
            }
        )

    # =====================================================
    # Reset
    # =====================================================

    def idle(self):

        self.state.status = HUD_IDLE

        self.state.listening = False
        self.state.speaking = False
        self.state.thinking = False
        self.state.executing = False

        self._publish(
            HUD_IDLE
        )


# Global manager

hud = HUDManager()