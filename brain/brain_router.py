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

from brain.developer.memory.developer_memory import (
    DeveloperMemory,
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

    Developer requests are separated into:

        CREATE
            ↓
        Developer Pipeline

        EDIT
            ↓
        Active Project
            ↓
        Developer Editor
    """

    # ------------------------------------------------------
    # Developer request indicators
    # ------------------------------------------------------

    DEVELOPER_WORDS = {

        "code",
        "file",
        "files",

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

        "create",
        "build",
        "make",
        "generate",
        "develop",
        "write",

        "arduino",
        "esp32",
        "esp8266",

        "sql",

        "calculator",
        "website",
        "webapp",
        "application",
        "app",

        "script",
        "program",
        "project",
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

    # ======================================================
    # Init
    # ======================================================

    def __init__(self):

        self.developer = Developer()

        self.developer_memory = DeveloperMemory()

        self.project_resolver = (
            ActiveProjectResolver(
                self.developer_memory,
            )
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

        CREATE requests do not require an active project.

        EDIT requests require an active project.
        """

        # --------------------------------------------------
        # Empty input
        # --------------------------------------------------

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
        # Developer request detected
        # --------------------------------------------------

        print(
            "[BRAIN ROUTER] "
            "Developer request detected."
        )

        # ==================================================
        # CREATE
        # ==================================================

        if self._is_create_request(
            command,
        ):

            print(
                "[BRAIN ROUTER] "
                "Developer CREATE request."
            )

            result = self.developer.execute(
                command,
                "",
            )

            if result is None:

                return BrainResult(
                    handled=False,
                    module="developer",
                    result=None,
                )

            return BrainResult(
                handled=True,
                module="developer",
                result=result,
            )

        # ==================================================
        # EDIT
        # ==================================================

        print(
            "[BRAIN ROUTER] "
            "Developer EDIT request."
        )

        project_path = (
            self.project_resolver.resolve()
        )

        # --------------------------------------------------
        # No active project
        # --------------------------------------------------

        if not project_path:

            print(
                "[BRAIN ROUTER] "
                "Developer edit request detected, "
                "but no active project is configured."
            )

            return BrainResult(
                handled=False,
                module="developer",
                result=None,
            )

        # --------------------------------------------------
        # Execute Developer Editor
        # --------------------------------------------------

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
    # Create Detection
    # ======================================================

    def _is_create_request(
        self,
        command: str,
    ) -> bool:
        """
        Determine whether a Developer request
        is asking for a new project.
        """

        text = command.lower().strip()

        create_actions = {

            "create",
            "build",
            "make",
            "generate",
            "develop",

        }

        words = set(
            text
            .replace(",", " ")
            .replace(".", " ")
            .split()
        )

        return bool(
            words & create_actions
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

        Supports both editing and creation
        requests.
        """

        text = command.lower().strip()

        # --------------------------------------------------
        # Explicit Developer phrases
        # --------------------------------------------------

        for phrase in self.DEVELOPER_PHRASES:

            if phrase in text:

                return True

        # --------------------------------------------------
        # Developer actions
        # --------------------------------------------------

        developer_actions = {

            "create",
            "build",
            "make",
            "develop",
            "implement",

            "add",
            "remove",
            "delete",

            "update",
            "modify",
            "change",

            "fix",
            "repair",

            "refactor",
            "optimize",

            "rename",
            "replace",

            "edit",
            "write",
            "generate",

        }

        # --------------------------------------------------
        # Developer context
        # --------------------------------------------------

        code_context = {

            "code",
            "file",
            "files",

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
            "c",

            "arduino",
            "esp32",
            "esp8266",

            "sql",

            "calculator",
            "website",
            "webapp",
            "application",
            "app",

            "script",
            "program",
            "project",

        }

        # --------------------------------------------------
        # Tokenize
        # --------------------------------------------------

        words = set(
            text
            .replace(",", " ")
            .replace(".", " ")
            .split()
        )

        has_action = bool(
            words & developer_actions
        )

        has_context = bool(
            words & code_context
        )

        # --------------------------------------------------
        # Developer request
        # --------------------------------------------------

        if has_action and has_context:

            return True

        return False

    # ======================================================
    # Active Project
    # ======================================================

    def configure_project(
        self,
        project_path: str,
    ) -> bool:
        """
        Configure the active Developer project.
        """

        return self.project_resolver.configure(
            project_path,
        )