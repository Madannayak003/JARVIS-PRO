"""
JARVIS PRO
Stage 5

Intent Engine

Central routing engine for deciding
how a user request should be processed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntentResult:
    mode: str
    confidence: float
    reason: str


class IntentEngine:

    CHAT_PREFIXES = {

        "what",
        "who",
        "where",
        "when",
        "why",
        "how",

        "tell",
        "describe",
        "define",
        "explain",

        "compare",
        "difference",

        "continue",

        "summarize",

        "can you",
        "could you",
        "would you",

        "do you know",

        "please"
    }

    CHAT_KEYWORDS = {

        # Coding
        "code",
        "python",
        "java",
        "javascript",
        "html",
        "css",
        "c++",
        "c#",
        "sql",

        "function",
        "class",
        "algorithm",
        "example",
        "project",
        "script",

        # AI
        "generate",
        "write",
        "create code",
        "sample code",

        # Learning
        "learn",
        "tutorial",
        "guide",

        # Conversation
        "joke",
        "story",
        "poem",

        # Explanation
        "meaning",
        "definition",

        # Follow-up
        "continue",
        "yes",
        "no",
        "okay",
        "ok",
        "thanks",
        "thank",
        "thank you"
    }

    ACTION_PREFIXES = {

        "open",
        "launch",
        "close",
        "shutdown",
        "restart",

        "search",

        "play",

        "stop",

        "delete",

        "copy",

        "move",

        "rename",

        "send",

        "call",

        "turn on",
        "turn off",

        "increase",
        "decrease"
    }

    def __init__(self, state=None):

        self.state = state

    # --------------------------------------------------

    def detect(self, command: str) -> IntentResult:

        command = command.lower().strip()

        # --------------------------------------------------
        # Conversation State (future integration)
        # --------------------------------------------------

        if self.state:

            try:

                if self.state.is_waiting():

                    owner = self.state.owner()

                    return IntentResult(
                        mode=owner,
                        confidence=1.0,
                        reason="conversation_state"
                    )

            except Exception:
                pass

        # --------------------------------------------------
        # Planner
        # --------------------------------------------------

        for prefix in self.ACTION_PREFIXES:

            if command.startswith(prefix):

                return IntentResult(
                    mode="planner",
                    confidence=0.98,
                    reason=f"action_prefix:{prefix}"
                )

        # --------------------------------------------------
        # Chat Prefix
        # --------------------------------------------------

        for prefix in self.CHAT_PREFIXES:

            if command.startswith(prefix):

                return IntentResult(
                    mode="chat",
                    confidence=0.97,
                    reason=f"chat_prefix:{prefix}"
                )

        # --------------------------------------------------
        # Chat Keyword
        # --------------------------------------------------

        for keyword in self.CHAT_KEYWORDS:

            if keyword in command:

                return IntentResult(
                    mode="chat",
                    confidence=0.95,
                    reason=f"chat_keyword:{keyword}"
                )

        # --------------------------------------------------
        # Default
        # --------------------------------------------------

        return IntentResult(
            mode="planner",
            confidence=0.50,
            reason="default"
        )