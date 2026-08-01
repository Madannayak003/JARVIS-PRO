from brain.developer.analyzer.detectors.project_detector import ProjectDetector


def main():

    detector = ProjectDetector()

    tests = [

        "Create Python console calculator",

        "Build Flask API",

        "Generate HTML portfolio website",

        "Create ESP32 weather station",

        "Build PyQt desktop application",

        "Create Python automation bot",

        "Write utility script",

        "Hello Jarvis",

    ]

    for text in tests:

        context = detector.create_context(text)
        result = detector.detect(context)

        print(f"{text:<45} -> {result}")


if __name__ == "__main__":
    main()