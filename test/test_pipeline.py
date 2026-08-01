import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from brain.profile_manager import ProfileManager
from brain.conversation_manager import ConversationManager
from brain.context_builder import ContextBuilder
from brain.prompt_builder import PromptBuilder
from brain.ai_pipeline import AIPipeline


class DummyLLM:

    def generate(self, prompt):

        print()

        print("=" * 60)

        print(prompt)

        print("=" * 60)

        print()

        return "Dummy AI Response"


profile = ProfileManager()

conversation = ConversationManager()

builder = ContextBuilder(profile, conversation)

prompt = PromptBuilder()

pipeline = AIPipeline(

    conversation,

    profile,

    builder,

    prompt,

    DummyLLM()

)

response = pipeline.process(

    "Continue Stage 4"

)

print()

print(response)