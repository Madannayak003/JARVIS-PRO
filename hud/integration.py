"""
JARVIS PRO
HUD Integration Layer

Safe one-way integration between JARVIS runtime
and the HUD system.

IMPORTANT:

JARVIS controls the HUD.

HUD NEVER controls JARVIS.

This module is intentionally passive.

When integration is disabled, every method becomes
a no-op and the existing JARVIS runtime is unaffected.
"""

from .emitter import HUDEmitter
from .event_contract import HUDEvent
from .runtime import hud_runtime

from config.hud_settings import HUD_ENABLED


# ============================================================
# Configuration
# ============================================================

HUD_ENABLED


# ============================================================
# HUD Integration
# ============================================================

class HUDIntegration:

    """
    Safe bridge used by the JARVIS runtime.

    The runtime can report events through this class
    without knowing anything about HUDManager, HUDState,
    or the UI implementation.
    """

    # --------------------------------------------------------
    # Internal event sender
    # --------------------------------------------------------

    @staticmethod
    def _emit(event, data=None):

        if not HUD_ENABLED:

            return

        try:

            HUDEmitter.emit(
                event,
                data
            )

        except Exception as e:

            # HUD failure must NEVER crash JARVIS.

            print(
                "[HUD INTEGRATION] "
                f"HUD event failed: {e}"
            )

    # ========================================================
    # Voice
    # ========================================================

    @classmethod
    def listening(cls):

        cls._emit(
            HUDEvent.LISTENING
        )

    @classmethod
    def speaking(cls):

        cls._emit(
            HUDEvent.SPEAKING
        )

    @classmethod
    def idle(cls):

        cls._emit(
            HUDEvent.IDLE
        )

    # ========================================================
    # AI
    # ========================================================

    @classmethod
    def thinking(cls):

        cls._emit(
            HUDEvent.THINKING
        )

    @classmethod
    def ai_model(
        cls,
        provider,
        model
    ):

        cls._emit(
            HUDEvent.AI_MODEL_CHANGED,
            {
                "provider": provider,
                "model": model
            }
        )

    # ========================================================
    # Tasks
    # ========================================================

    @classmethod
    def task_started(cls, task):

        cls._emit(
            HUDEvent.TASK_STARTED,
            {
                "task": task
            }
        )

    @classmethod
    def executing(cls, task=""):

        cls._emit(
            HUDEvent.EXECUTING,
            {
                "task": task
            }
        )

    @classmethod
    def task_finished(cls, task=""):

        cls._emit(
            HUDEvent.TASK_FINISHED,
            {
                "task": task
            }
        )

    @classmethod
    def task_failed(
        cls,
        task="",
        error=""
    ):

        cls._emit(
            HUDEvent.TASK_FAILED,
            {
                "task": task,
                "error": error
            }
        )
        
    # ========================================================
    # Runtime
    # ========================================================

    @classmethod
    def start(cls):

        if not HUD_ENABLED:

            return

        try:

            hud_runtime.start()

            print(
                "[MAIN HUD] HUD runtime started."
            )

        except Exception as e:

            print(
                "[HUD INTEGRATION] "
                f"HUD runtime failed: {e}"
            )

    @classmethod
    def stop(cls):

        if not HUD_ENABLED:

            return

        try:

            hud_runtime.stop()

        except Exception as e:

            print(
                "[HUD INTEGRATION] "
                f"HUD runtime stop failed: {e}"
            )

    # ========================================================
    # Voice Mode
    # ========================================================

    @classmethod
    def voice_mode(cls, mode):

        cls._emit(
            HUDEvent.VOICE_MODE_CHANGED,
            {
                "mode": mode
            }
        )

    # ========================================================
    # System
    # ========================================================

    @classmethod
    def system_update(cls, data):

        cls._emit(
            HUDEvent.SYSTEM_UPDATE,
            data
        )

    # ========================================================
    # Notifications
    # ========================================================

    @classmethod
    def notify(cls, message):

        cls._emit(
            HUDEvent.NOTIFICATION,
            {
                "message": message
            }
        )

    @classmethod
    def error(cls, message):

        cls._emit(
            HUDEvent.ERROR,
            {
                "message": message
            }
        )

    # ========================================================
    # Status
    # ========================================================

    @classmethod
    def enabled(cls):

        return HUD_ENABLED