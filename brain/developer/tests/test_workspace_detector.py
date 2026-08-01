from brain.developer.analyzer.detectors.workspace_detector import WorkspaceDetector


def main():

    detector = WorkspaceDetector()

    tests = [

        "Create Python calculator",

        "Build Flask API",

        "Generate HTML website",

        "Create React dashboard",

        "Build Arduino robot",

        "Create ESP32 weather station",

        "Hello Jarvis"

    ]

    for text in tests:

        context = detector.create_context(text)
        result = detector.detect(context)

        print(f"{text:<40} -> {result}")


if __name__ == "__main__":
    main()