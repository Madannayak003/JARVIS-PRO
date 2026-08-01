"""
JARVIS PRO

Prompt Builder Test
"""

from brain.developer.analyzer import Analyzer
from brain.developer.planner import Planner
from brain.developer.prompt_builder import PromptBuilder


def main():

    analyzer = Analyzer()

    planner = Planner()

    prompt_builder = PromptBuilder()

    tests = [

        "Create Python calculator",

        "Build Flask REST API",

        "Generate React dashboard",

        "Create ESP32 weather station",

        "Build Arduino Uno robot",

        "Create Next.js portfolio website",

    ]

    for text in tests:

        analysis = analyzer.analyze(text)

        plan = planner.create_plan(analysis)

        result = prompt_builder.build(

            user_request=text,

            analysis=analysis,

            execution_plan=plan,

        )

        print("=" * 80)

        print(text)

        print()

        print("SYSTEM PROMPT")

        print("-" * 80)

        print(result.system_prompt)

        print()

        print("USER PROMPT")

        print("-" * 80)

        print(result.user_prompt)

        print()

        print("FINAL PROMPT")

        print("-" * 80)

        print(result.prompt)

        print()


if __name__ == "__main__":

    main()