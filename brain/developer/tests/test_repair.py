"""
JARVIS PRO

Validator Test
"""

from brain.developer.pipeline import DeveloperPipeline


def main():

    pipeline = DeveloperPipeline()

    context = pipeline.process(

        "Create a Python calculator"

    )

    result = context.validation_result

    print("\n" + "=" * 80)
    print("VALIDATION REPORT")
    print("=" * 80)

    print()

    print("Valid          :", result.valid)
    print("Score          :", result.score)

    print()

    print("Total Checks   :", result.total_checks)
    print("Passed Checks  :", result.passed_checks)
    print("Failed Checks  :", result.failed_checks)

    print()

    print("Warnings       :", result.warning_count)
    print("Errors         :", result.error_count)
    print("Critical       :", result.critical_count)

    print()

    print("Generated      :", context.generated_project.generated)
    print("Files          :", len(context.generated_project.files))

    print()

    if result.issues:

        print("=" * 80)
        print("ISSUES")
        print("=" * 80)

        for issue in result.issues:

            print()

            print(f"[{issue.level.name}]")

            print("Validator :", issue.validator)

            if issue.file:
                print("File      :", issue.file)

            print("Message   :", issue.message)

            if issue.expected:
                print("Expected  :", issue.expected)

            if issue.actual:
                print("Actual    :", issue.actual)

            if issue.suggestion:
                print("Suggestion:", issue.suggestion)

    else:

        print("=" * 80)
        print("NO VALIDATION ISSUES")
        print("=" * 80)
        
        print()

        print("=" * 80)

        print("REPAIR RESULT")

        print("=" * 80)

        if context.repair_result:

            print("Success :", context.repair_result.success)

            print("Files   :", context.repair_result.repaired_files)

            if context.repair_result.errors:

                print()

                print("Errors:")

                for error in context.repair_result.errors:

                    print("-", error)

        else:

            print("Repair was not executed.")


if __name__ == "__main__":

    main()