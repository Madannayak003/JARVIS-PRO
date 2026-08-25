"""
JARVIS PRO
Phase 11.3.8

Generic Follow-Up Execution Bridge

Converts an understood conversational follow-up into
an existing JARVIS action.

IMPORTANT:

This module does NOT:

    - execute commands directly
    - call the planner
    - call an AI model
    - replace the dispatcher
    - replace fast routing
    - modify existing skills

It only translates a resolved conversational follow-up
into an existing action plan.
"""

from __future__ import annotations

from typing import Optional


class FollowUpExecutionBridge:

    # ========================================================
    # Resolve
    # ========================================================

    def resolve(
        self,
        *,
        raw_input: str,
        follow_up,
    ) -> Optional[list[dict]]:

        # ----------------------------------------------------
        # No follow-up
        # ----------------------------------------------------

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

        # ====================================================
        # Determine active domain
        # ====================================================

        domain = (
            application
            or skill
            or ""
        ).lower().strip()

        # ====================================================
        # SPOTIFY
        # ====================================================

        if domain == "spotify":

            # ------------------------------------------------
            # Volume Up
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Volume Down
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Pause
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Resume
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Next
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Previous
            # ------------------------------------------------

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

        # ====================================================
        # YOUTUBE
        # ====================================================

        if domain == "youtube":

            # ------------------------------------------------
            # Play First Video
            # ------------------------------------------------

            if command in [
                "play the first one",
                "play first one",
                "play the first video",
                "play first video",
            ]:

                return [
                    {
                        "action":
                            "youtube_play_first"
                    }
                ]
                
            # ------------------------------------------------
            # Volume Up
            # ------------------------------------------------

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
                        "action": "volume",
                        "direction": "up",
                    }
                ]

            # ------------------------------------------------
            # Volume Down
            # ------------------------------------------------

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
                        "action": "volume",
                        "direction": "down",
                    }
                ]

            # ------------------------------------------------
            # Pause
            # ------------------------------------------------

            if command in [
                "pause it",
                "pause that",
                "pause the video",
                "pause",
            ]:

                return [
                    {
                        "action":
                            "youtube_pause"
                    }
                ]

            # ------------------------------------------------
            # Resume
            # ------------------------------------------------

            if command in [
                "resume",
                "resume it",
                "resume that",
                "resume the video",
                "resume youtube",
                "resume youtube video",
                "continue it",
                "continue the video",
                "continue youtube",
                "play it",
                "play it again",
            ]:

                return [
                    {
                        "action":
                            "youtube_resume"
                    }
                ]

            # ------------------------------------------------
            # Next
            # ------------------------------------------------

            if command in [
                "next",
                "next video",
                "next one",
                "play the next video",
                "play the next one",
            ]:

                return [
                    {
                        "action":
                            "youtube_next"
                    }
                ]

            # ------------------------------------------------
            # Previous
            # ------------------------------------------------

            if command in [
                "previous",
                "previous video",
                "previous one",
                "go back",
                "play the previous video",
                "play the previous one",
            ]:

                return [
                    {
                        "action":
                            "youtube_previous"
                    }
                ]

        # ====================================================
        # BROWSER / APPLICATION
        # ====================================================

        if domain == "browser":

            if command in [
                "close it",
                "close that",
                "close this",
                "exit it",
                "exit that",
            ]:

                browser_applications = {
                    "chrome",
                    "edge",
                    "firefox",
                    "brave",
                    "opera",
                }

                if application in browser_applications:

                    return [
                        {
                            "action": "close"
                        }
                    ]
        
        # ================================================
        # SYSTEM
        # ====================================================

        if domain == "system":

            # ------------------------------------------------
            # Volume Up
            # ------------------------------------------------

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
                        "action": "volume",
                        "direction": "up",
                    }
                ]

            # ------------------------------------------------
            # Volume Down
            # ------------------------------------------------

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
                        "action": "volume",
                        "direction": "down",
                    }
                ]
                
        # =====================================================
        # Windows / System Applications
        # =====================================================

        if (
            application in [
                "notepad",
                "calculator",
                "calc",
                "paint",
                "cmd",
                "command prompt",
                "powershell",
                "explorer",
                "file explorer",
                "task manager",
                "registry editor",
                "device manager",
                "control panel",
                "settings",
            ]
        ):

            # -------------------------------------------------
            # Close current application
            # -------------------------------------------------

            if command in [
                "close it",
                "close that",
                "close this",
                "exit it",
                "exit that",
            ]:

                process = application

                if application == "calc":
                    process = "calculator"

                if application == "command prompt":
                    process = "cmd"

                if application == "file explorer":
                    process = "explorer"

                if application == "task manager":
                    process = "taskmgr"

                return [
                    {
                        "action": "close_process",
                        "process": process,
                    }
                ]

        # =====================================================
        # System Volume
        # =====================================================

        if (
            application == "system"
            or skill == "system"
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
                        "action": "volume",
                        "direction": "up",
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
                        "action": "volume",
                        "direction": "down",
                    }
                ]

        # ====================================================
        # No known follow-up
        # ====================================================

        return None


# ============================================================
# Shared Bridge
# ============================================================

followup_execution_bridge = (
    FollowUpExecutionBridge()
)