from brain.profile_manager import ProfileManager
from brain.conversation_manager import ConversationManager
from brain.context_builder import ContextBuilder

profile = ProfileManager()

conversation = ConversationManager()

conversation.add_user_message("Hello")

conversation.add_assistant_message("Hi!")

conversation.add_user_message("Continue JARVIS")

builder = ContextBuilder(
    profile,
    conversation
)

context = builder.build(
    "Continue Stage 4"
)

print()

print("User Input")
print(context.user_input)

print()

print("Profile")
print(context.profile["name"])

print()

print("Conversation")

for msg in context.conversation:
    print(msg["role"], ":", msg["content"])

print()

print("Project")

print(context.project)

print()

print("Metadata")

print(context.metadata)