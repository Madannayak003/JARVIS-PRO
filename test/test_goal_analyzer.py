from brain.goal_analyzer import GoalAnalyzer

brain = GoalAnalyzer()

tests = [

    "write python calculator",

    "open chrome",

    "search youtube for arduino",

    "tell me a joke"

]

for t in tests:

    print()

    print(t)

    print(brain.analyze(t))