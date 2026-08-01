from brain.developer.developer_detector import DeveloperDetector
from brain.developer.developer_defaults import DeveloperDefaultsEngine

detector = DeveloperDetector()
defaults = DeveloperDefaultsEngine()

tests = [

    "Write Python calculator",

    "Create HTML portfolio",

    "Build Flask API",

    "Generate Arduino project"

]

for command in tests:

    print("\n" + "=" * 60)

    print(command)

    req = detector.detect(command)

    result = defaults.build(req)

    print()

    print(result)