from brain.developer.analyzer.detectors.intent_detector import IntentDetector


def main():

    detector = IntentDetector()

    tests = [

        "Create a Python calculator",

        "Build an ESP32 weather station",

        "Generate HTML website",

        "Edit my Flask API",

        "Update this project",

        "Fix my Python code",

        "Delete this file",

        "Explain Python decorators",

        "Analyze this repository",

        "Hello Jarvis"

    ]

    for text in tests:

        context = detector.create_context(text)
        result = detector.detect(context)

        print(f"{text:<35} -> {result}")


if __name__ == "__main__":
    main()