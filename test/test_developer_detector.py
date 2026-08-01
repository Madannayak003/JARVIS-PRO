from brain.developer.developer_detector import DeveloperDetector

detector = DeveloperDetector()

tests = [

    "Write Python calculator",

    "Create HTML portfolio",

    "Build Flask API",

    "Generate React login page",

    "Create Arduino traffic light",

    "Write calculator code",

    "Make a dashboard"

]

for t in tests:

    print("\n", "="*60)

    print(t)

    print(detector.detect(t))