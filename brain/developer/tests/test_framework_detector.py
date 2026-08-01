from brain.developer.analyzer.detectors.framework_detector import FrameworkDetector


def main():

    detector = FrameworkDetector()

    tests = [

        "Create Flask API",

        "Build Django website",

        "Make React dashboard",

        "Generate FastAPI backend",

        "Create Vue application",

        "Build Angular admin panel",

        "Create Next.js portfolio",

        "Build Express server",

        "Write Python calculator",

    ]

    for text in tests:

        context = detector.create_context(text)
        result = detector.detect(context)

        print(f"{text:<35} -> {result}")


if __name__ == "__main__":
    main()