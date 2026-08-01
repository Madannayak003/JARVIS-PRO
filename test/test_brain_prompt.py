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

profile = ProfileManager()

conversation = ConversationManager()

conversation.add_user_message("Hello")

conversation.add_assistant_message("Hi Madan!")

conversation.add_user_message("Continue JARVIS PRO")

builder = ContextBuilder(profile, conversation)

context = builder.build("Build Stage 4")

prompt = PromptBuilder().build(context)

print(prompt)