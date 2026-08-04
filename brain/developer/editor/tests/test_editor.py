from brain.developer.editor.analyzer import EditAnalyzer
from brain.developer.editor.planner import EditPlanner
from brain.developer.editor.prompt_builder import PromptBuilder

from brain.developer.generator.providers.ollama_provider import (
    OllamaProvider,
)


def main():

    analyzer = EditAnalyzer()

    planner = EditPlanner()

    prompt_builder = PromptBuilder()
    
    provider = OllamaProvider()

    project = "workspace/Python/PythonCalculator"

    tests = [

        # Existing functions
        "Fix divide()",
        "Optimize multiply()",
        "Rename add() to addition()",
        "Rename calculator to simple_calculator",

        # New feature
        "Add modulo() function",

        # Formatting
        "Format main.py",      

        # Documentation
        "Update README.md",

    ]

    for command in tests:

        result = analyzer.analyze(

            command,

            project,

        )
        
        print("=" * 80)
        print("PROJECT INDEX")
        print("=" * 80)

        if result.project_index:

            print("Files      :", result.project_index.files)
            print("Functions  :", sorted(result.project_index.functions.keys()))
            print("Classes    :", sorted(result.project_index.classes.keys()))
            print("Imports    :", sorted(result.project_index.imports.keys()))

        print()

        result = planner.plan(

            result,

        )

        prompt = prompt_builder.build(

            result,

        )
        
        response = provider.generate(

            prompt,

        )

        print("=" * 60)
        print("Request        :", command)
        print("Action         :", result.edit_type)
        print("Instructions   :", result.instructions)
        print("Selected Files :", result.target_files)
        
        print()

        print("FILE CONTENT SENT TO OLLAMA")
        print("-" * 80)

        for file, content in result.file_contents.items():

            print(file)
            print("-" * 80)

            print(content)

            print("=" * 80)

        print("=" * 80)
        print(prompt.prompt)
        
        print("=" * 80)
        print("RAW AI RESPONSE")
        print("=" * 80)
        print(response)


if __name__ == "__main__":

    main()