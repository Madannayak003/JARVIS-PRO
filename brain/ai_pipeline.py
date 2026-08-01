"""
JARVIS PRO
Stage 4 - AI Pipeline

Central AI Brain Pipeline

Author: Madan
"""

from __future__ import annotations

from typing import Callable


class AIPipeline:

    def __init__(
        self,
        conversation_manager,
        profile_manager,
        context_builder,
        prompt_builder,
        llm=None,
        memory_manager=None
    ):

        self.conversation = conversation_manager
        self.profile = profile_manager
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder

        self.llm = llm
        self.memory = memory_manager

    # ==========================================================
    # Normal Response (Testing / Future REST API)
    # ==========================================================

    def process(self, user_input: str):

        if self.llm is None:
            raise RuntimeError("No synchronous LLM configured.")

        self.conversation.add_user_message(user_input)

        context = self.context_builder.build(user_input)

        prompt = self.prompt_builder.build(context)

        response = self.llm.generate(prompt)

        self.conversation.add_assistant_message(response)

        self._store_memory(user_input, response)

        return response

    # ==========================================================
    # Streaming Response (Real JARVIS)
    # ==========================================================

    def process_stream(
        self,
        user_input: str,
        stream_callback: Callable,
        system_prompt: str,
        stop_event=None
    ):

        # --------------------------------------------
        # Save user message
        # --------------------------------------------

        self.conversation.add_user_message(user_input)

        # --------------------------------------------
        # Build Context
        # --------------------------------------------

        context = self.context_builder.build(user_input)

        # --------------------------------------------
        # Build Prompt
        # --------------------------------------------

        prompt = self.prompt_builder.build(context)

        # --------------------------------------------
        # Start Streaming
        # --------------------------------------------

        stream = stream_callback(
            system_prompt,
            prompt,
            stop_event
        )

        complete_response = []

        for chunk in stream:

            if not isinstance(chunk, dict):
                continue

            text = chunk.get("response", "")

            if text:
                complete_response.append(text)

            # Pass original chunk to existing code
            yield chunk

        # --------------------------------------------
        # Save Assistant Reply
        # --------------------------------------------

        final_response = "".join(complete_response).strip()

        if final_response:

            self.conversation.add_assistant_message(
                final_response
            )

            self._store_memory(
                user_input,
                final_response
            )

    # ==========================================================
    # Long-Term Memory
    # ==========================================================

    def _store_memory(
        self,
        user_input: str,
        assistant_response: str
    ):

        if self.memory is None:
            return

        try:

            if hasattr(self.memory, "store"):

                self.memory.store(

                    user=user_input,

                    assistant=assistant_response

                )

        except Exception as e:

            print(f"[Brain Memory] {e}")