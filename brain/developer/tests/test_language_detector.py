from brain.developer.analyzer.detectors.language_detector import LanguageDetector


def main():

    detector = LanguageDetector()

    tests = [

        "Create a Python calculator",

        "Build a C++ compiler",

        "Write Java application",

        "Generate HTML website",

        "Create JavaScript game",

        "Build TypeScript API",

        "Write Dart Flutter app",

        "Create Rust CLI",

        "Build Go server",

        "Hello Jarvis"

    ]

    for text in tests:

        context = detector.create_context(text)
        result = detector.detect(context)

        print(f"{text:<35} -> {result}")


if __name__ == "__main__":
    main()