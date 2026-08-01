"""
JARVIS PRO
Brain Singleton

Creates one shared AI Brain instance
used throughout the application.
"""

from brain.conversation_manager import ConversationManager
from brain.profile_manager import ProfileManager
from brain.context_builder import ContextBuilder
from brain.prompt_builder import PromptBuilder
from brain.ai_pipeline import AIPipeline
from brain.conversation_state import ConversationStateManager


class Brain:

    def __init__(self):

        # --------------------------------------------
        # Brain Information
        # --------------------------------------------

        self.version = "1.0"

        self.initialized = False

        # --------------------------------------------
        # Core Managers
        # --------------------------------------------

        self.conversation = ConversationManager()

        self.profile = ProfileManager()

        self.state = ConversationStateManager()

        # --------------------------------------------
        # Context Builder
        # --------------------------------------------

        self.context_builder = ContextBuilder(
            self.profile,
            self.conversation
        )

        # --------------------------------------------
        # Prompt Builder
        # --------------------------------------------

        self.prompt_builder = PromptBuilder()

        # --------------------------------------------
        # AI Pipeline
        # --------------------------------------------

        self.pipeline = AIPipeline(
            conversation_manager=self.conversation,
            profile_manager=self.profile,
            context_builder=self.context_builder,
            prompt_builder=self.prompt_builder
        )

        # --------------------------------------------
        # Brain Ready
        # --------------------------------------------

        self.initialized = True


# ==================================================
# Shared Brain Instance (Singleton)
# ==================================================

brain = Brain()

# ==================================================
# Convenience Exports
# ==================================================

pipeline = brain.pipeline

conversation = brain.conversation

profile = brain.profile

state = brain.state