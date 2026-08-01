from brain.developer.developer_service import DeveloperService

service = DeveloperService()

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

    result = service.handle(command)

    print(result)

    print()

    print("Handled     :", result.handled)
    print("Developer   :", result.developer)
    print("Action      :", result.action)
    print("Project     :", result.project_name)
    print("Found       :", result.project_found)
    print("Parsed      :", result.parsed_files)
    print("Merged      :", result.merged)

    print()