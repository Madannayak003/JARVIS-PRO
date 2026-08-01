"""
JARVIS PRO

Workspace Test
"""

#  python -m brain.developer.tests.test_workspace

from brain.developer.pipeline import DeveloperPipeline


def main():

    pipeline = DeveloperPipeline()

    context = pipeline.process(

        # "create a python calculator"
        # "Create a Arduino RFID door lock"
        "Create an ESP32 weather station using WiFi"
        # "Create a personal portfolio website"
        #  "Create a React Todo App"
        # "Create a Flask login system"

    )

    print("\n" + "=" * 80)
    print("WORKSPACE RESULT")
    print("=" * 80)
    
    
    print("\n" + "=" * 80)
    print("VALIDATION RESULT")
    print("=" * 80)

    validation = context.validation_result

    if validation is None:

        print("Validation was not executed.")

        return

    print("Valid :", validation.valid)
    print("Score :", validation.score)

    print()

    for issue in validation.issues:

        print(f"[{issue.level.name}]")

        print("Validator :", issue.validator)

        print("Message   :", issue.message)

        if issue.expected:

            print("Expected  :", issue.expected)

        if issue.actual:

            print("Actual    :", issue.actual)

        if issue.suggestion:

            print("Suggestion:", issue.suggestion)

        print()
    
    

    if context.workspace_result is None:

        print("Workspace was not executed.")

        return

    result = context.workspace_result

    print()

    print("Success      :", result.success)

    print("Project Name :", result.project_name)

    print("Project Path :", result.project_path)

    print("Folders      :", result.folder_count)

    print("Files        :", result.file_count)

    print("Bytes        :", result.bytes_written)

    print()

    if result.errors:

        print("Errors")

        print("-" * 80)

        for error in result.errors:

            print(error)

        print()


if __name__ == "__main__":

    main()