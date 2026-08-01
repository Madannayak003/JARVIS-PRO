from brain.developer.developer_chat import DeveloperChat

chat = DeveloperChat()

tests = [

    "Write Python calculator",

    "Create HTML portfolio",

    "Build Flask API",

    "Tell me a joke",

    "What is cloud computing?",

    "Write calculator code"

]

for command in tests:

    print("=" * 70)

    print(command)

    result = chat.prepare(command)

    print(result)

    print()