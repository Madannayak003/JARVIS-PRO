"""
JARVIS PRO
Stage 4 - Prompt Builder

Builds the final prompt sent to the LLM.

Author: Madan
"""

from __future__ import annotations

from typing import List

from .context_types import AIContext


class PromptBuilder:

    def __init__(self):

        self.system_prompt = """
You are JARVIS PRO.

You are an intelligent AI assistant designed to help the user with coding,
automation, planning, research, electronics, IoT, robotics and productivity.

Rules:

- Be accurate.
- Be concise unless detailed explanation is requested.
- Continue conversations naturally.
- Use previous conversation when relevant.
- Use user profile when appropriate.
- Never invent facts.
- If information is missing, ask.
""".strip()

    # --------------------------------------------------

    def _profile_section(self, context: AIContext) -> str:

        profile = context.profile

        return f"""
========== USER PROFILE ==========

Name: {profile.get("name","")}

Preferred Language: {profile.get("preferred_language","")}

Coding Language: {profile.get("coding_language","")}

IDE: {profile.get("ide","")}

Current Project: {profile.get("current_project","")}

Response Style: {profile.get("response_style","")}
""".strip()

    # --------------------------------------------------

    def _conversation_section(self, context: AIContext) -> str:

        if not context.conversation:

            return ""

        lines: List[str] = []

        lines.append("========== RECENT CONVERSATION ==========")

        for msg in context.conversation:

            role = msg["role"].capitalize()

            content = msg["content"]

            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    # --------------------------------------------------

    def _memory_section(self, context: AIContext) -> str:

        if not context.memories:

            return ""

        lines = []

        lines.append("========== RELEVANT MEMORIES ==========")

        for memory in context.memories:

            lines.append(str(memory))

        return "\n".join(lines)

    # --------------------------------------------------

    def _planner_section(self, context: AIContext) -> str:

        if not context.planner:

            return ""

        return f"""
========== PLANNER STATE ==========
{context.planner}
""".strip()

    # --------------------------------------------------

    def _project_section(self, context: AIContext) -> str:

        return f"""
========== CURRENT PROJECT ==========

Project:
{context.project.get("name","")}
""".strip()

    # --------------------------------------------------

    def _user_input_section(self, context: AIContext) -> str:

        return f"""
========== CURRENT REQUEST ==========

{context.user_input}
""".strip()

    # --------------------------------------------------

    def build(self, context: AIContext) -> str:

        sections = [

            self.system_prompt,

            self._profile_section(context),

            self._project_section(context),

            self._conversation_section(context),

            self._memory_section(context),

            self._planner_section(context),

            self._user_input_section(context)

        ]

        sections = [

            section

            for section in sections

            if section.strip()

        ]

        return "\n\n".join(sections)