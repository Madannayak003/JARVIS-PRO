from brain.developer.developer_assistant import DeveloperAssistant

assistant = DeveloperAssistant()

tests = [

    "Write Python calculator",

    "Create HTML portfolio",

    "Build Flask API",

    "Generate Arduino traffic light",

    "Write calculator code",

    "Tell me a joke"

]

for command in tests:

    print("\n" + "=" * 70)

    print(command)

    result = assistant.process(command)

    print(result)

    if result.enhanced_prompt:

        print("\n------------ PROMPT ------------\n")

        print(result.enhanced_prompt)