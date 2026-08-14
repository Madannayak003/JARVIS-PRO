"""
JARVIS PRO
Natural Conversation Intelligence

NCI-5: Response Strategy

Determines HOW JARVIS should handle an understood request.

This layer does NOT execute anything.

It only decides:

    - conversation
    - action
    - hybrid
    - clarification

and whether AI reasoning is useful.
"""

from dataclasses import dataclass
from enum import Enum


# ============================================================
# Response Mode
# ============================================================

class ResponseMode(Enum):

    CONVERSATION = "conversation"

    ACTION = "action"

    HYBRID = "hybrid"

    CLARIFICATION = "clarification"


# ============================================================
# Response Strategy
# ============================================================

@dataclass(frozen=True)
class ResponseStrategy:

    mode: ResponseMode

    needs_action: bool

    needs_ai: bool

    needs_clarification: bool

    intent: str

    confidence: float

    reason: str


# ============================================================
# NCI-5 Engine
# ============================================================

class ResponseStrategyEngine:

    def decide(self, meaning):

        # ====================================================
        # Clarification
        # ====================================================

        if meaning.intent == "clarification":

            return ResponseStrategy(

                mode=ResponseMode.CLARIFICATION,

                needs_action=False,

                needs_ai=False,

                needs_clarification=True,

                intent=meaning.intent,

                confidence=0.94,

                reason=(
                    "The user is requesting "
                    "clarification."
                ),
            )

        # ====================================================
        # Hybrid
        # ====================================================

        if meaning.intent == "hybrid_request":

            return ResponseStrategy(

                mode=ResponseMode.HYBRID,

                needs_action=True,

                needs_ai=True,

                needs_clarification=False,

                intent=meaning.intent,

                confidence=0.93,

                reason=(
                    "The request contains both "
                    "an executable action and "
                    "a conversational requirement."
                ),
            )

        # ====================================================
        # Explicit action
        # ====================================================

        if meaning.mode.value == "action":

            return ResponseStrategy(

                mode=ResponseMode.ACTION,

                needs_action=True,

                needs_ai=False,

                needs_clarification=False,

                intent=meaning.intent,

                confidence=0.94,

                reason=(
                    "The request is an executable "
                    "action and does not require "
                    "conversational reasoning."
                ),
            )

        # ====================================================
        # Conversation
        # ====================================================

        if meaning.mode.value == "conversation":

            return ResponseStrategy(

                mode=ResponseMode.CONVERSATION,

                needs_action=False,

                needs_ai=True,

                needs_clarification=False,

                intent=meaning.intent,

                confidence=0.94,

                reason=(
                    "The request requires a "
                    "natural conversational response."
                ),
            )

        # ====================================================
        # Safe fallback
        # ====================================================

        return ResponseStrategy(

            mode=ResponseMode.CONVERSATION,

            needs_action=False,

            needs_ai=True,

            needs_clarification=False,

            intent=(
                meaning.intent
                or "unknown"
            ),

            confidence=0.60,

            reason=(
                "No specific response strategy "
                "was identified."
            ),
        )


# ============================================================
# Shared engine
# ============================================================

response_strategy_engine = (
    ResponseStrategyEngine()
)