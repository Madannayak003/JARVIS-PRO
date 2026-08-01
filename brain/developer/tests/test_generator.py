"""
JARVIS PRO

Generator Test
"""

from brain.developer.pipeline import DeveloperPipeline


def main():

    pipeline = DeveloperPipeline()

    request = "Create a Python calculator"

    context = pipeline.process(request)

    project = context.generated_project

    print("=" * 80)

    print("PROJECT")

    print("=" * 80)

    print()

    print("Generated :", project.generated)

    print("Files     :", len(project.files))

    print()

    for file in project.files:

        print("-" * 60)

        print(file.path)

        print()

        print(file.content[:400])

        print()


if __name__ == "__main__":

    main()