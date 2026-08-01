from brain.developer.developer_intent import DeveloperIntentDetector

detector = DeveloperIntentDetector()

tests = [

    "create python calculator",

    "build portfolio",

    "update calculator",

    "fix login page",

    "add firebase",

    "continue calculator",

    "open calculator",

    "delete calculator"

]

for t in tests:

    print("=" * 60)

    print(t)

    print(detector.detect(t))