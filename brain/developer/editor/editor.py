"""
JARVIS PRO
Developer Editor

Main Editor Engine
"""

from brain.developer.editor.analyzer import EditAnalyzer

from brain.developer.editor.planner import EditPlanner

from brain.developer.editor.prompt_builder import PromptBuilder

from brain.developer.generator.providers.ollama_provider import (
    OllamaProvider,
)

from brain.developer.editor.parser import ResponseParser

from brain.developer.editor.validator.edit_validator import (
    EditValidator,
)

from brain.developer.editor.workspace.patch_writer import (
    PatchWriter,
)


class Editor:
    """
    Main Developer Editor engine.
    """

    def __init__(self):

        self.analyzer = EditAnalyzer()

        self.planner = EditPlanner()

        self.prompt_builder = PromptBuilder()

        self.provider = OllamaProvider()

        self.parser = ResponseParser()

        self.validator = EditValidator()

        self.writer = PatchWriter()

    # --------------------------------------------------

    def execute(

        self,

        user_request: str,

        project_path: str,

    ):

        # ------------------------------------------
        # Analyze
        # ------------------------------------------

        request = self.analyzer.analyze(

            user_request,

            project_path,

        )

        # ------------------------------------------
        # Plan
        # ------------------------------------------

        plan  = self.planner.plan(

            request,

        )

        # ------------------------------------------
        # Build Prompt
        # ------------------------------------------

        prompt = self.prompt_builder.build(

            plan,

        )

        # ------------------------------------------
        # Generate
        # ------------------------------------------

        response = self.provider.generate(

            prompt,

        )

        # ------------------------------------------
        # Parse
        # ------------------------------------------

        result = self.parser.parse(

            response,

        )

        # ------------------------------------------
        # Validate
        # ------------------------------------------

        result = self.validator.validate(

            result,

        )

        if not result.success:

            return result

        # ------------------------------------------
        # Write
        # ------------------------------------------

        self.writer.write(

            project_path,

            result.patches,

        )

        return result