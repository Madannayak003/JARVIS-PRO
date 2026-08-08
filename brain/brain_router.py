"""
JARVIS PRO
Brain Router

Phase 10.2

Routes requests to the correct subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass

from brain.developer import Developer

from brain.developer.integration.active_project import (
    ActiveProjectResolver,
)


# ==========================================================
# Result
# ==========================================================

@dataclass
class BrainResult:

    handled: bool = False
    module: str = ""
    result: object | None = None


# ==========================================================
# Router
# ==========================================================

class BrainRouter:
    """
    Routes user requests to the appropriate subsystem.

    Phase 10.2:
        Connect existing-project Developer requests
        to the Developer Editor.
    """

    # ------------------------------------------------------
    # Developer request indicators
    # ------------------------------------------------------

    DEVELOPER_WORDS = {

        "code",
        "file",
        "function",
        "class",
        "python",
        "javascript",
        "typescript",
        "html",
        "css",
        "react",
        "cpp",
        "c++",

        "edit",
        "modify",
        "change",
        "update",
        "fix",
        "repair",
        "refactor",
        "rename",
        "replace",
        "remove",
        "delete",
        "implement",
        "insert",
        "add",

    }

    DEVELOPER_PHRASES = (

        "fix code",
        "fix the code",

        "edit code",
        "edit the code",

        "modify code",
        "modify the code",

        "change code",
        "change the code",

        "update code",
        "update the code",

        "refactor code",
        "refactor the code",

        "add function",
        "add a function",

        "create function",
        "create a function",

        "change function",
        "modify function",

        "fix function",
        "fix the function",

    )

    # ------------------------------------------------------

    def __init__(self):

        self.developer = Developer()

        self.project_resolver = (
            ActiveProjectResolver()
        )

    # ======================================================
    # Route
    # ======================================================

    def route(
        self,
        user_input: str,
    ) -> BrainResult:
        """
        Route a JARVIS request.

        Normal requests are left untouched.

        Developer requests are sent to the
        existing Developer Editor when an
        active project is available.
        """

        if not user_input:

            return BrainResult(
                handled=False,
            )

        command = user_input.strip()

        if not command:

            return BrainResult(
                handled=False,
            )

        # --------------------------------------------------
        # Developer detection
        # --------------------------------------------------

        if not self._is_developer_request(
            command,
        ):

            return BrainResult(
                handled=False,
            )

        # --------------------------------------------------
        # Resolve active project
        # --------------------------------------------------

        project_path = (
            self.project_resolver.resolve()
        )

        if not project_path:

            print(
                "[BRAIN ROUTER] "
                "Developer request detected, "
                "but no active project is configured."
            )

            return BrainResult(
                handled=False,
                module="developer",
                result=None,
            )

        # --------------------------------------------------
        # Execute Developer
        # --------------------------------------------------

        print(
            "[BRAIN ROUTER] "
            "Developer request detected."
        )

        result = self.developer.execute(
            command,
            project_path,
        )

        return BrainResult(
            handled=True,
            module="developer",
            result=result,
        )

    # ======================================================
    # Developer Detection
    # ======================================================

    def _is_developer_request(
        self,
        command: str,
    ) -> bool:
        """
        Determine whether a command is intended
        for the Developer subsystem.

        Uses explicit developer phrases first,
        then checks for code-related terminology.
        """

        text = command.lower().strip()

        # --------------------------------------------------
        # Explicit phrases
        # --------------------------------------------------

        for phrase in self.DEVELOPER_PHRASES:

            if phrase in text:

                return True

        # --------------------------------------------------
        # Token matching
        # --------------------------------------------------

        words = set(
            text.replace(
                ",",
                " ",
            ).replace(
                ".",
                " ",
            ).split()
        )

        # --------------------------------------------------
        # Editing action + code context
        # --------------------------------------------------

        edit_actions = {

            "edit",
            "modify",
            "change",
            "update",
            "fix",
            "repair",
            "refactor",
            "rename",
            "replace",
            "remove",
            "delete",
            "implement",
            "insert",
            "add",

        }

        code_context = {

            "code",
            "file",
            "function",
            "class",
            "python",
            "javascript",
            "typescript",
            "html",
            "css",
            "react",
            "cpp",
            "c++",

        }

        has_action = bool(
            words & edit_actions
        )

        has_context = bool(
            words & code_context
        )

        if has_action and has_context:

            return True

        return False