"""
JARVIS PRO
Stage 4 - Context Builder

Builds a unified AIContext object by collecting data from
Conversation Manager, Profile Manager and Memory Manager.

Author: Madan
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .context_types import AIContext


class ContextBuilder:

    def __init__(
        self,
        profile_manager,
        conversation_manager,
        memory_manager=None,
        planner=None
    ):
        """
        Parameters
        ----------
        profile_manager
            ProfileManager instance

        conversation_manager
            ConversationManager instance

        memory_manager
            Existing memory system (optional)

        planner
            Planner instance (optional)
        """

        self.profile = profile_manager
        self.conversation = conversation_manager
        self.memory = memory_manager
        self.planner = planner

    # --------------------------------------------------------

    def build(
        self,
        user_input: str,
        memory_limit: int = 5,
        conversation_limit: int = 10
    ) -> AIContext:

        context = AIContext()

        # ----------------------------------------------------
        # Current user request
        # ----------------------------------------------------

        context.user_input = user_input

        # ----------------------------------------------------
        # User profile
        # ----------------------------------------------------

        context.profile = self.profile.as_dict()

        # ----------------------------------------------------
        # Recent conversation
        # ----------------------------------------------------

        messages = self.conversation.get_recent_messages(
            conversation_limit
        )

        context.conversation = [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp
            }
            for m in messages
        ]

        # ----------------------------------------------------
        # Long-term memory
        # ----------------------------------------------------

        context.memories = []

        if self.memory is not None:

            try:

                memories = self.memory.search(
                    user_input,
                    limit=memory_limit
                )

                context.memories = memories

            except Exception:

                # Keep JARVIS running even if memory fails
                context.memories = []

        # ----------------------------------------------------
        # Planner state
        # ----------------------------------------------------

        context.planner = {}

        if self.planner is not None:

            try:

                if hasattr(self.planner, "get_state"):

                    context.planner = self.planner.get_state()

            except Exception:

                context.planner = {}

        # ----------------------------------------------------
        # Active project
        # ----------------------------------------------------

        context.project = {

            "name": context.profile.get(
                "current_project",
                ""
            ),

            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            )
        }

        # ----------------------------------------------------
        # Tool information
        # ----------------------------------------------------

        context.tools = {}

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        context.metadata = {

            "builder": "ContextBuilder",

            "version": "1.0",

            "conversation_messages":
                len(context.conversation),

            "memory_results":
                len(context.memories),

            "generated_at":
                datetime.now().isoformat(
                    timespec="seconds"
                )
        }

        return context