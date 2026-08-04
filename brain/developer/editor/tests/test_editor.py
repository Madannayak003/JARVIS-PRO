from brain.developer.editor.analyzer import EditAnalyzer


def main():

    analyzer = EditAnalyzer()

    project = "workspace/Python/PythonCalculator"

    tests = [

        "Add login page",
        "Fix RFID code",
        "Rename login() to signIn()",
        "Replace Firebase with Supabase",
        "Optimize parser",
        "Format main.py",

    ]

    for command in tests:

        result = analyzer.analyze(

            command,

            project,

        )

        print("=" * 60)
        print("Request      :", command)
        print("Action       :", result.edit_type)
        print("Instructions :", result.instructions)
        print("Target Files :", result.target_files)


if __name__ == "__main__":

    main()