from brain.developer.analysis.analyzer import ProjectAnalyzer


def main():

    analyzer = ProjectAnalyzer()

    spec = analyzer.analyze(
        "Create an ESP32 weather station using WiFi Firebase MQTT"
    )

    print("=" * 60)

    print("Intent       :", spec.intent)
    print("Language     :", spec.language)
    print("Framework    :", spec.framework)
    print("Board        :", spec.board)
    print("Runtime      :", spec.runtime)
    print("Workspace    :", spec.workspace)
    print("Project Type :", spec.project_type)

    print()

    print("Technologies")

    for tech in spec.technologies:
        print("-", tech)


if __name__ == "__main__":
    main()