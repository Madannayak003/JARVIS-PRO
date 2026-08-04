from brain.developer.editor.analyzer import EditAnalyzer
from brain.developer.editor.planner import EditPlanner


def main():

    analyzer = EditAnalyzer()
    planner = EditPlanner()

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

        # -------------------------
        # Analyze
        # -------------------------

        result = analyzer.analyze(

            command,

            project,

        )

        # -------------------------
        # Plan
        # -------------------------

        result = planner.plan(

            result,

        )

        print("=" * 60)
        print("Request        :", command)
        print("Action         :", result.edit_type)
        print("Instructions   :", result.instructions)
        print("Selected Files :", result.target_files)


if __name__ == "__main__":

    main()