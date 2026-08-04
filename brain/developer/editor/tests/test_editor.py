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

        print("=" * 80)
        print(prompt.prompt)
        
        print("=" * 80)
        print("RAW AI RESPONSE")
        print("=" * 80)
        print(response)


if __name__ == "__main__":

    main()