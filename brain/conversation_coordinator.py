"""
JARVIS PRO
Phase 11.3.6

Conversation Coordinator

Connects the Phase 11.3 Natural Conversation components
without changing the existing JARVIS execution pipeline.

IMPORTANT:

OBSERVATION / UNDERSTANDING ONLY.

This module must NOT:

    - dispatch commands
    - execute skills
    - call planner
    - change confirmation behavior
    - change WhatsApp behavior
    - change busy-manager behavior
    - change wake-word behavior
    - change sleep/wake behavior
    - change memory behavior

It only observes user input and updates conversational
understanding/context.

Existing JARVIS execution remains authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from brain.conversation_understanding import (
    ConversationUnderstandingEngine,
    ConversationUnderstanding,
)

from brain.conversation_context import (
    ConversationContextManager,
    conversation_context,
)


from brain.reference_resolver import (
    ReferenceResolver,
    ReferenceResolution,
)

from brain.followup_resolver import (
    FollowUpResolver,
    FollowUpResolution,
)

from brain.clarification_manager import (
    ClarificationManager,
)

# ============================================================
# Coordinator Result
# ============================================================

@dataclass
class ConversationAnalysis:

    # --------------------------------------------------------
    # Original input
    # --------------------------------------------------------

    raw_input: str = ""

    # --------------------------------------------------------
    # Understanding
    # --------------------------------------------------------

    understanding: Optional[
        ConversationUnderstanding
    ] = None

    # --------------------------------------------------------
    # Follow-up resolution
    # --------------------------------------------------------

    follow_up: Optional[
        FollowUpResolution
    ] = None

    # --------------------------------------------------------
    # Reference resolutions
    # --------------------------------------------------------

    references: dict[str, ReferenceResolution] = None

    # --------------------------------------------------------
    # Clarification state
    # --------------------------------------------------------

    clarification_waiting: bool = False

    clarification_field: Optional[str] = None

    clarification_question: Optional[str] = None

    # --------------------------------------------------------
    # Context snapshot
    # --------------------------------------------------------

    context: dict[str, Any] = None


# ============================================================
# Conversation Coordinator
# ============================================================

class ConversationCoordinator:

    def __init__(
        self,
        conversation_manager=None,
        state_manager=None,
        context_manager=None,
        understanding_engine=None,
        reference_resolver=None,
        follow_up_resolver=None,
        clarification_manager=None,
    ):

        # ----------------------------------------------------
        # Existing conversation history
        # ----------------------------------------------------

        self.conversation = (
            conversation_manager
        )

        # ----------------------------------------------------
        # Existing ConversationStateManager
        # ----------------------------------------------------

        self.state = state_manager

        # ----------------------------------------------------
        # New natural conversation context
        # ----------------------------------------------------

        self.context = (
            context_manager
            if context_manager is not None
            else conversation_context
        )

        # ----------------------------------------------------
        # Understanding
        # ----------------------------------------------------

        self.understanding = (
            understanding_engine
            or ConversationUnderstandingEngine()
        )

        # ----------------------------------------------------
        # Reference resolver
        # ----------------------------------------------------

        self.reference_resolver = (
            reference_resolver
            or ReferenceResolver()
        )

        # ----------------------------------------------------
        # Follow-up resolver
        # ----------------------------------------------------

        self.follow_up = (
            follow_up_resolver
            or FollowUpResolver(
                self.reference_resolver
            )
        )

        # ----------------------------------------------------
        # Clarification manager
        # ----------------------------------------------------

        self.clarification = (
            clarification_manager
            or ClarificationManager()
        )

    # ========================================================
    # Analyze Input
    # ========================================================

    def analyze(
        self,
        user_input: str,
    ) -> ConversationAnalysis:

        raw_input = user_input or ""
        
        print(
            "[CONVERSATION DEBUG] analyze context:",
            id(self.context)
        )

        print(
            "[CONVERSATION DEBUG] analyze context snapshot:",
            self.context.snapshot()
        )

        # ----------------------------------------------------
        # Update last input
        # ----------------------------------------------------

        self.context.set_user_input(
            raw_input
        )

        # ----------------------------------------------------
        # Existing conversation history
        #
        # Read-only.
        # ----------------------------------------------------

        previous_messages = None

        if self.conversation is not None:

            try:

                previous_messages = (
                    self.conversation
                    .get_recent_messages(
                        limit=10
                    )
                )

            except Exception:

                previous_messages = None

        # ----------------------------------------------------
        # Conversation understanding
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Determine conversational waiting state
        #
        # Existing ConversationStateManager remains
        # authoritative for existing JARVIS task ownership.
        #
        # New ClarificationManager is also checked because
        # Natural Conversation needs to recognize answers
        # such as:
        #
        #     "google"
        #     "Rahul"
        #     "yes"
        #     "Chrome"
        #
        # as answers when JARVIS is explicitly waiting
        # for clarification.
        # ----------------------------------------------------

        understanding_state = self.state

        try:

            if self.clarification.is_waiting():

                understanding_state = (
                    self.clarification
                )

        except Exception as e:

            print(
                "[CONVERSATION] "
                f"Clarification state check failed: {e}"
            )


        understanding = (
            self.understanding.understand(

                user_input=raw_input,

                previous_messages=(
                    previous_messages
                ),

                state=understanding_state,

            )
        )

        # ----------------------------------------------------
        # Save relationship
        # ----------------------------------------------------

        self.context.set_relation(
            understanding.relation.value
        )

        # ----------------------------------------------------
        # Resolve references
        # ----------------------------------------------------

        reference_results = {}

        for reference in (
            understanding.references or []
        ):

            try:

                result = (
                    self.reference_resolver.resolve(

                        reference,

                        self.context,

                    )
                )

                reference_results[
                    reference
                ] = result

            except Exception as e:

                print(
                    "[CONVERSATION] "
                    f"Reference error: {e}"
                )

        # ----------------------------------------------------
        # Follow-up resolution
        # ----------------------------------------------------

        follow_up = None

        try:

            follow_up = (
                self.follow_up.resolve(

                    understanding,

                    self.context,

                )
            )

        except Exception as e:

            print(
                "[CONVERSATION] "
                f"Follow-up error: {e}"
            )

        # ----------------------------------------------------
        # Clarification state
        # ----------------------------------------------------

        clarification_waiting = False

        clarification_field = None

        clarification_question = None

        try:

            clarification_waiting = (
                self.clarification.is_waiting()
            )

            if clarification_waiting:

                clarification_field = (
                    self.clarification.field()
                )

                clarification_question = (
                    self.clarification.question()
                )

        except Exception as e:

            print(
                "[CONVERSATION] "
                f"Clarification error: {e}"
            )

        # ----------------------------------------------------
        # Build analysis result
        # ----------------------------------------------------

        return ConversationAnalysis(

            raw_input=raw_input,

            understanding=understanding,

            follow_up=follow_up,

            references=reference_results,

            clarification_waiting=(
                clarification_waiting
            ),

            clarification_field=(
                clarification_field
            ),

            clarification_question=(
                clarification_question
            ),

            context=self.context.snapshot(),

        )

    # ========================================================
    # Observe Input
    # ========================================================

    def observe(
        self,
        user_input: str,
    ) -> ConversationAnalysis:

        """
        Safe observation mode.

        This method performs analysis only.

        It does NOT change JARVIS execution.
        """

        try:

            return self.analyze(
                user_input
            )

        except Exception as e:

            # ------------------------------------------------
            # Critical safety rule:
            #
            # Natural Conversation must NEVER break the
            # existing JARVIS runtime.
            # ------------------------------------------------

            print(
                "[CONVERSATION] "
                f"Analysis failed safely: {e}"
            )

            return ConversationAnalysis(
                raw_input=user_input or "",
                context=self.context.snapshot(),
            )

    # ========================================================
    # Update Context After Execution
    # ========================================================

    def record_execution(
        self,
        *,
        topic=None,
        task=None,
        application=None,
        skill=None,
        intent=None,
        action=None,
        object=None,
        objects=None,
        result=None,
    ):

        """
        Records information AFTER an existing JARVIS
        component has successfully processed a command.

        This does not execute anything.

        This method will be used later when we know exactly
        what the existing dispatcher/planner returns.
        """

        self.context.update(

            topic=topic,

            task=task,

            application=application,

            skill=skill,

            intent=intent,

            action=action,

            object=object,

            objects=objects,

            last_result=result,

        )
        
        print(
            "[CONVERSATION DEBUG] record_execution context:",
            id(self.context)
        )

        print(
            "[CONVERSATION DEBUG] context after execution:",
            self.context.snapshot()
        )

    # ========================================================
    # Record Assistant Response
    # ========================================================

    def record_response(
        self,
        response: str,
    ):

        self.context.set_assistant_response(
            response
        )

    # ========================================================
    # Start Clarification
    # ========================================================

    def start_clarification(
        self,
        field: str,
        question: str,
        task=None,
        owner=None,
        metadata=None,
    ):

        self.clarification.start(

            field=field,

            question=question,

            task=task,

            owner=owner,

            metadata=metadata,

        )

        self.context.set_pending_question(
            question
        )

        self.context.set_pending_clarification(
            field
        )

    # ========================================================
    # Resolve Clarification
    # ========================================================

    def resolve_clarification(
        self,
        value,
    ):

        result = (
            self.clarification.resolve(
                value
            )
        )

        if result is not None:

            self.context.clear_pending()

        return result

    # ========================================================
    # Clear
    # ========================================================

    def clear(self):

        self.context.clear()

        self.clarification.clear()

    # ========================================================
    # Debug Info
    # ========================================================

    def info(self) -> dict:

        return {

            "context":
                self.context.snapshot(),

            "clarification":
                self.clarification.info(),

        }


# ============================================================
# Shared Coordinator
# ============================================================

from brain.brain import brain


conversation_coordinator = (
    ConversationCoordinator(

        conversation_manager=(
            brain.conversation
        ),

        state_manager=(
            brain.state
        ),

        context_manager=(
            brain.conversation_context
        ),
    )
)