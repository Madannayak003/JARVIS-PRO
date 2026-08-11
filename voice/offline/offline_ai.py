"""
JARVIS PRO
Offline AI Brain

Completely isolated offline AI layer.

Pipeline:

Offline STT
    ↓
ContextBuilder
    ↓
PromptBuilder
    ↓
Ollama
    ↓
Offline TTS

IMPORTANT:
This module never uses:
- OpenAI
- Gemini
- Edge TTS
- Google STT
- Internet
- voice.manager
"""

import requests

from brain.profile_manager import ProfileManager
from brain.conversation_manager import ConversationManager
from brain.context_builder import ContextBuilder
from brain.prompt_builder import PromptBuilder


# =========================================================
# Configuration
# =========================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

OLLAMA_MODEL = "jarvis"

OLLAMA_TIMEOUT = 120

# =========================================================
# Offline Voice Instructions
# =========================================================

OFFLINE_VOICE_INSTRUCTIONS = """
You are JARVIS PRO operating in OFFLINE VOICE MODE.

You are speaking directly to the user.

Response rules:
- Give short, natural spoken answers.
- Normally answer in 1 to 3 sentences.
- Prefer 1 or 2 sentences for simple questions.
- Do not give long explanations unless the user explicitly asks for details.
- Do not use Markdown headings.
- Do not use bullet points unless specifically requested.
- Do not use tables.
- Do not repeat the user's question.
- Speak naturally and conversationally.
- Use the user's profile, conversation context, project context, and memories when relevant.
- Never invent information.
"""


# =========================================================
# Offline Brain
# =========================================================

class OfflineAI:

    def __init__(self):

        print("[OFFLINE AI] Initializing...")

        # -------------------------------------------------
        # Existing Stage 4 components
        # -------------------------------------------------

        self.profile = ProfileManager()

        self.conversation = ConversationManager()

        self.context_builder = ContextBuilder(
            profile_manager=self.profile,
            conversation_manager=self.conversation,
            memory_manager=None,
            planner=None,
        )

        self.prompt_builder = PromptBuilder()

        print("[OFFLINE AI] Stage 4 context ready.")

    # =====================================================
    # Ollama
    # =====================================================

    def _ollama(self, prompt):

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }

        try:

            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=OLLAMA_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            text = data.get(
                "response",
                ""
            ).strip()

            return text

        except Exception as e:

            print(
                "[OFFLINE AI ERROR]",
                e
            )

            return None

    # =====================================================
    # Ask
    # =====================================================

    def ask(self, user_input):

        if not user_input:

            return None

        user_input = str(
            user_input
        ).strip()

        if not user_input:

            return None

        print(
            "[OFFLINE AI] Building context..."
        )

        # -------------------------------------------------
        # Build existing Stage 4 context
        # -------------------------------------------------

        context = self.context_builder.build(
            user_input
        )

        # -------------------------------------------------
        # Build existing Stage 4 prompt
        # -------------------------------------------------

        base_prompt = self.prompt_builder.build(
            context
        )

        prompt = (
            base_prompt
            + "\n\n"
            + OFFLINE_VOICE_INSTRUCTIONS
        )

        print(
            "[OFFLINE AI] Thinking..."
        )

        # -------------------------------------------------
        # Local Ollama
        # -------------------------------------------------

        response = self._ollama(
            prompt
        )

        if not response:

            return None

        # -------------------------------------------------
        # Save conversation
        # -------------------------------------------------

        self.conversation.add_user_message(
            user_input
        )

        self.conversation.add_assistant_message(
            response
        )

        return response


# =========================================================
# Singleton
# =========================================================

_ai = None


def get_ai():

    global _ai

    if _ai is None:

        _ai = OfflineAI()

    return _ai


# =========================================================
# Simple API
# =========================================================

def ask(user_input):

    return get_ai().ask(
        user_input
    )