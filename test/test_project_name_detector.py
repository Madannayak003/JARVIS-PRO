from brain.developer.project_name_detector import ProjectNameDetector

detector = ProjectNameDetector()

tests = [

    "create python calculator",

    "update calculator",

    "edit portfolio",

    "fix login page",

    "continue jarvis",

    "open weather app",

    "delete todo app",

    "build react ecommerce website",

    "make html portfolio",

    "create esp32 weather station"

]

for t in tests:

    result = detector.detect(t)

    print("=" * 60)
    print(t)
    print(result)