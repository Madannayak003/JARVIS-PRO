from brain.developer.developer_controller import DeveloperController

controller = DeveloperController()

tests = [

    "create python calculator",

    "update calculator",

    "open calculator",

    "continue calculator",

    "delete calculator"

]

for command in tests:

    print("=" * 60)

    print(command)

    print()

    result = controller.handle(command)

    print(result)

    print()

    print("Action      :", result.action)

    print("Project     :", result.project_name)

    print("Found       :", result.project_found)

    print("Developer   :", result.developer)

    print("Handled     :", result.handled)

    print("Merged      :", result.merged)

    print("Files       :", result.parsed_files)

    print()