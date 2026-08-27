"""
JARVIS PRO
HUD Adapter

Safe integration layer between JARVIS and the HUD.

IMPORTANT:

This adapter only reports information to the HUD.

It must NEVER:

- execute JARVIS commands
- control the AI
- control voice
- control Developer Mode
- control skills
- modify core runtime behavior
"""

from .manager import hud


class HUDAdapter:

    # =====================================================
    # Voice
    # =====================================================

    @staticmethod
    def listening():

        hud.listening()

    @staticmethod
    def thinking():

        hud.thinking()

    @staticmethod
    def speaking():

        hud.speaking()

    @staticmethod
    def idle():

        hud.idle()

    # =====================================================
    # Conversation
    # =====================================================

    @staticmethod
    def command(text):

        hud.command(
            text
        )

    @staticmethod
    def response(text):

        hud.response(
            text
        )

    # =====================================================
    # Tasks
    # =====================================================

    @staticmethod
    def task_started(task):

        hud.task_started(
            task
        )

    @staticmethod
    def executing(task=""):

        hud.executing(
            task
        )

    @staticmethod
    def task_finished(task=""):

        hud.task_finished(
            task
        )

    @staticmethod
    def task_failed(
        task="",
        error=""
    ):

        hud.task_failed(
            task,
            error
        )

    # =====================================================
    # AI
    # =====================================================

    @staticmethod
    def ai_model(
        provider,
        model
    ):

        hud.ai_model(
            provider,
            model
        )

    # =====================================================
    # Voice Mode
    # =====================================================

    @staticmethod
    def voice_mode(mode):

        hud.voice_mode(
            mode
        )

    # =====================================================
    # System
    # =====================================================

    @staticmethod
    def system_update(data):

        hud.system_update(
            data
        )

    # =====================================================
    # Notifications
    # =====================================================

    @staticmethod
    def notify(message):

        hud.notify(
            message
        )

    @staticmethod
    def error(message):

        hud.error(
            message
        )