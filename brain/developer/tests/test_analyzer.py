from brain.developer.analyzer import Analyzer


def main():

    analyzer = Analyzer()

    tests = [

        "Create Python calculator",

        "Build Flask REST API",

        "Generate React dashboard",

        "Create ESP32 weather station",

        "Build Arduino Uno robot",

        "Create Next.js portfolio website",

        "Build Python desktop application",

    ]

    for text in tests:

        result = analyzer.analyze(text)

        print("=" * 70)

        print(text)

        print()

        print("Intent      :", result.intent)

        print("Language    :", result.language)

        print("Framework   :", result.framework)

        print("Workspace   :", result.workspace)

        print("ProjectType :", result.project_type)

        print("Runtime     :", result.runtime)

        print("Board       :", result.board)


if __name__ == "__main__":
    main()