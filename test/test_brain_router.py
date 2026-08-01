from brain.brain_router import BrainRouter

router = BrainRouter()

tests = [

    "hello",

    "create python calculator",

    "update calculator",

    "continue calculator",

    "delete calculator"

]

for command in tests:

    print("=" * 60)
    print(command)
    print()

    result = router.route(command)

    print("Handled :", result.handled)
    print("Module  :", result.module)

    if result.result:

        print("Action  :", result.result.action)
        print("Project :", result.result.project_name)

    print()