"""
JARVIS PRO
Phase 11.3.7

Follow-Up Execution Bridge

Converts an understood conversational follow-up into
an existing JARVIS action.

IMPORTANT:

This module does NOT:
    - execute commands directly
    - call the planner
    - call an AI model
    - replace the dispatcher
    - replace fast routing

It only translates a resolved conversational follow-up
into an existing action plan.
"""

from __future__ import annotations

from typing import Optional


class FollowUpExecutionBridge:

    def resolve(
        self,
        *,
        raw_input: str,
        follow_up,
    ) -> Optional[list[dict]]:

        if not follow_up:
            return None

        if not follow_up.is_follow_up:
            return None

        command = (
            raw_input
            .lower()
            .strip()
        )

        application = (
            follow_up.application
        )

        skill = (
            follow_up.skill
        )

        # =====================================================
        # Spotify
        # =====================================================

        if (
            application == "spotify"
            or skill == "spotify"
        ):

            # -------------------------------------------------
            # Volume up
            # -------------------------------------------------

            if command in [
                "make it louder",
                "make that louder",
                "increase the volume",
                "turn it up",
                "turn that up",
                "louder",
                "volume up",
                "increase volume",
            ]:

                return [
                    {
                        "action":
                            "spotify_volume_up"
                    }
                ]

            # -------------------------------------------------
            # Volume down
            # -------------------------------------------------

            if command in [
                "make it quieter",
                "make that quieter",
                "decrease the volume",
                "turn it down",
                "turn that down",
                "quieter",
                "volume down",
                "decrease volume",
            ]:

                return [
                    {
                        "action":
                            "spotify_volume_down"
                    }
                ]

            # -------------------------------------------------
            # Pause
            # -------------------------------------------------

            if command in [
                "pause it",
                "pause that",
                "pause the music",
                "stop the music",
            ]:

                return [
                    {
                        "action":
                            "spotify_pause"
                    }
                ]

            # -------------------------------------------------
            # Resume
            # -------------------------------------------------

            if command in [
                "resume it",
                "resume that",
                "continue it",
                "continue the music",
                "play it again",
            ]:

                return [
                    {
                        "action":
                            "spotify_play"
                    }
                ]

            # -------------------------------------------------
            # Next
            # -------------------------------------------------

            if command in [
                "next",
                "next one",
                "play the next one",
                "skip it",
                "skip this",
            ]:

                return [
                    {
                        "action":
                            "spotify_next"
                    }
                ]

            # -------------------------------------------------
            # Previous
            # -------------------------------------------------

            if command in [
                "previous",
                "previous one",
                "go back",
                "play the previous one",
            ]:

                return [
                    {
                        "action":
                            "spotify_previous"
                    }
                ]

        # =====================================================
        # No known follow-up
        # =====================================================

        return None


# ============================================================
# Shared Bridge
# ============================================================

followup_execution_bridge = (
    FollowUpExecutionBridge()
)