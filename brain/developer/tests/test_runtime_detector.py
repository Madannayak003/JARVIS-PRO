from brain.developer.analyzer.detectors.runtime_detector import RuntimeDetector


def main():

    detector = RuntimeDetector()

    tests = [

        "Create Python desktop calculator",

        "Build Flask API",

        "Create React website",

        "Create ESP32 weather station",

        "Build Android application",

        "Hello Jarvis",

    ]

    for text in tests:

        context = detector.create_context(text)
        result = detector.detect(context)

        print(f"{text:<40} -> {result}")


if __name__ == "__main__":
    main()