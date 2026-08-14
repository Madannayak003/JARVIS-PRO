"""
JARVIS PRO
Natural Conversation Intelligence

NCI-6: Conversation Request Builder

Purpose
-------
Converts the output of NCI-2, NCI-4 and NCI-5 into a
structured request that the existing AI pipeline can use.

IMPORTANT:
    This module does NOT:
        - call Ollama
        - execute actions
        - modify the dispatcher
        - modify Fast Router
        - modify FollowUpResolver

It only prepares the meaning of the request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# ============================================================
# Conversation Request
# ============================================================

@dataclass(frozen=True)
class ConversationRequest:

    # --------------------------------------------------------
    # Original request
    # --------------------------------------------------------

    user_input: str

    # --------------------------------------------------------
    # NCI meaning
    # --------------------------------------------------------

    intent: str

    mode: str

    confidence: float

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    topic: Optional[str] = None

    task: Optional[str] = None

    object: Optional[str] = None

    reference: Optional[str] = None

    application: Optional[str] = None

    skill: Optional[str] = None

    # --------------------------------------------------------
    # Strategy
    # --------------------------------------------------------

    needs_ai: bool = False

    needs_action: bool = False

    needs_clarification: bool = False

    # --------------------------------------------------------
    # AI instructions
    # --------------------------------------------------------

    instructions: str = ""

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# Builder
# ============================================================

class ConversationRequestBuilder:

    """
    NCI-6 request builder.

    Takes:

        Natural Context
        Meaning Understanding
        Response Strategy

    and produces:

        ConversationRequest
    """

    # --------------------------------------------------------

    @staticmethod
    def _value(
        source,
        name: str,
        default=None
    ):
        """
        Safely read an attribute from an NCI object.
        """

        if source is None:

            return default

        return getattr(
            source,
            name,
            default
        )

    # --------------------------------------------------------

    def build(
        self,
        *,
        user_input: str,
        meaning,
        strategy,
        context=None
    ) -> ConversationRequest:

        # ====================================================
        # Meaning
        # ====================================================

        intent = self._value(
            meaning,
            "intent",
            "unknown"
        )

        confidence = float(
            self._value(
                meaning,
                "confidence",
                0.0
            )
        )

        # ====================================================
        # Strategy
        # ====================================================

        mode = self._value(
            strategy,
            "mode",
            None
        )

        if hasattr(mode, "value"):

            mode = mode.value

        mode = (
            str(mode)
            if mode is not None
            else "conversation"
        )

        needs_ai = bool(
            self._value(
                strategy,
                "needs_ai",
                False
            )
        )

        needs_action = bool(
            self._value(
                strategy,
                "needs_action",
                False
            )
        )

        needs_clarification = bool(
            self._value(
                strategy,
                "needs_clarification",
                False
            )
        )

        # ====================================================
        # Context
        # ====================================================

        topic = self._value(
            meaning,
            "topic"
        )

        task = self._value(
            meaning,
            "task"
        )

        object_value = self._value(
            meaning,
            "object"
        )

        reference = self._value(
            meaning,
            "reference"
        )

        application = self._value(
            meaning,
            "application"
        )

        skill = self._value(
            meaning,
            "skill"
        )

        # ----------------------------------------------------
        # If meaning doesn't contain context, use NCI context.
        # ----------------------------------------------------

        if context is not None:

            topic = (
                topic
                or self._value(
                    context,
                    "topic"
                )
            )

            task = (
                task
                or self._value(
                    context,
                    "task"
                )
            )

            object_value = (
                object_value
                or self._value(
                    context,
                    "object"
                )
            )

            application = (
                application
                or self._value(
                    context,
                    "application"
                )
            )

            skill = (
                skill
                or self._value(
                    context,
                    "skill"
                )
            )

        # ====================================================
        # Instructions
        # ====================================================

        instructions = (
            self._build_instructions(
                intent=intent,
                mode=mode,
                needs_ai=needs_ai,
                needs_action=needs_action,
                needs_clarification=(
                    needs_clarification
                ),
                topic=topic,
                task=task,
                object_value=object_value,
                reference=reference,
                application=application,
                skill=skill
            )
        )

        # ====================================================
        # Metadata
        # ====================================================

        metadata = {

            "builder":
                "ConversationRequestBuilder",

            "version":
                "1.0",

            "nci_stage":
                "NCI-6",

        }

        return ConversationRequest(

            user_input=user_input,

            intent=intent,

            mode=mode,

            confidence=confidence,

            topic=topic,

            task=task,

            object=object_value,

            reference=reference,

            application=application,

            skill=skill,

            needs_ai=needs_ai,

            needs_action=needs_action,

            needs_clarification=(
                needs_clarification
            ),

            instructions=instructions,

            metadata=metadata
        )

    # ========================================================
    # Instruction Builder
    # ========================================================

    @staticmethod
    def _build_instructions(
        *,
        intent,
        mode,
        needs_ai,
        needs_action,
        needs_clarification,
        topic,
        task,
        object_value,
        reference,
        application,
        skill
    ) -> str:

        instructions = []

        # ----------------------------------------------------
        # Conversation
        # ----------------------------------------------------

        if mode == "conversation":

            instructions.append(
                "Respond naturally as part of "
                "the ongoing conversation."
            )

            if topic:

                instructions.append(
                    f"Current topic: {topic}."
                )

            if task:

                instructions.append(
                    f"Current task: {task}."
                )

            if object_value:

                instructions.append(
                    f"Current subject: {object_value}."
                )

            if reference:

                instructions.append(
                    f"The user referenced: {reference}."
                )

        # ----------------------------------------------------
        # Action
        # ----------------------------------------------------

        elif mode == "action":

            instructions.append(
                "This request is primarily "
                "an executable action."
            )

            instructions.append(
                "Do not use AI reasoning when "
                "the existing execution system "
                "can handle the request."
            )

        # ----------------------------------------------------
        # Hybrid
        # ----------------------------------------------------

        elif mode == "hybrid":

            instructions.append(
                "This request contains both "
                "an executable action and a "
                "conversational requirement."
            )

            instructions.append(
                "Preserve both parts of the request."
            )

        # ----------------------------------------------------
        # Clarification
        # ----------------------------------------------------

        elif mode == "clarification":

            instructions.append(
                "The user needs clarification."
            )

            instructions.append(
                "Ask a concise clarification "
                "question before proceeding."
            )

        # ----------------------------------------------------
        # Application
        # ----------------------------------------------------

        if application:

            instructions.append(
                f"Active application: {application}."
            )

        # ----------------------------------------------------
        # Skill
        # ----------------------------------------------------

        if skill:

            instructions.append(
                f"Active skill: {skill}."
            )

        # ----------------------------------------------------
        # AI requirement
        # ----------------------------------------------------

        if needs_ai:

            instructions.append(
                "AI reasoning is required."
            )

        else:

            instructions.append(
                "AI reasoning is not required."
            )

        return " ".join(
            instructions
        )


# ============================================================
# Shared Builder
# ============================================================

conversation_request_builder = (
    ConversationRequestBuilder()
)