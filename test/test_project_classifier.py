from brain.developer.project.project_classifier import ProjectClassifier

classifier = ProjectClassifier()

tests = [

    "Create Arduino RFID Door Lock using MFRC522",

    "Generate HTML Login Page",

    "Build ESP32 Weather Station",

    "Create Python Calculator",

    "Make Bluetooth Car"

]

for t in tests:

    result = classifier.classify(t)

    print("=" * 60)

    print(t)

    print(result)