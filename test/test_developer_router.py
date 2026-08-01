from brain.developer.developer_router import DeveloperRouter

router = DeveloperRouter()

tests = [

    "hello",

    "what is python",

    "create python calculator",

    "update calculator",

    "continue calculator",

    "delete calculator",

]

for command in tests:

    print("=" * 60)

    print(command)

    print()

    result = router.route(command)

    print("Handled   :", result.handled)

    print("Developer :", result.developer)

    if result.workflow:

        print()

        print("Action    :", result.workflow.action)

        print("Project   :", result.workflow.project_name)

        print("Found     :", result.workflow.project_found)

        print("Merged    :", result.workflow.merged)

    print()