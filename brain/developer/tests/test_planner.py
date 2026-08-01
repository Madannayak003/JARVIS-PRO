"""
JARVIS PRO

Planner Test
"""

from brain.developer.analyzer import Analyzer
from brain.developer.planner import Planner


def main():

    analyzer = Analyzer()

    planner = Planner()

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

        analysis = analyzer.analyze(text)

        plan = planner.create_plan(analysis)

        print("=" * 70)

        print(text)

        print()

        print("Planner :", plan.__class__.__name__)

        print("Workspace:", plan.workspace)

        print("Folders :", plan.folders)

        print("Files   :", plan.files)

        print("Tasks   :", plan.tasks)


if __name__ == "__main__":

    main()