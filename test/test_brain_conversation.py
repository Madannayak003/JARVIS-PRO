from brain.conversation_manager import ConversationManager

conv = ConversationManager(max_messages=5)

conv.add_user_message("Hello")

conv.add_assistant_message("Hi Madan!")

conv.add_user_message("Open VS Code")

conv.add_assistant_message("Opening VS Code")

conv.add_user_message("Create Python file")

print()

print(conv)

print()

for msg in conv.get_recent_messages():

    print(msg.role, ":", msg.content)

conv.save_json()

print()

print("Conversation saved.")