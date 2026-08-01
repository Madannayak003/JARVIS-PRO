"""
JARVIS PRO
Developer Planner

Python Planner
"""

from brain.developer.enums import Language

from brain.developer.models.analysis_result import AnalysisResult

from brain.developer.planner.models.execution_plan import ExecutionPlan

from brain.developer.planner.planners.base_planner import BasePlanner


class PythonPlanner(BasePlanner):
    """
    Planner for Python projects.
    """

    def can_handle(self, analysis: AnalysisResult) -> bool:

        return analysis.language == Language.PYTHON

    def create_plan(self, analysis: AnalysisResult) -> ExecutionPlan:

        plan = self.create_base_plan(analysis)

        # -----------------------------
        # Default Python Structure
        # -----------------------------

        plan.folders = [

            "src",

            "tests",

            "docs",

        ]

        # plan.files = [

        #     "src/main.py",

        #     "tests/test_main.py",

        #     "docs/README.md",

        #     "requirements.txt",

        #     ".gitignore",

        # ]
        
        plan.files = [

            "src/main.py",

            "tests/test_main.py",

            "docs/README.md",

            "requirements.txt",

            ".gitignore",

            "LICENSE",

        ]

        plan.dependencies = []

        plan.tasks = [

            "Create project structure",

            "Generate source files",

            "Install dependencies",

        ]

        plan.notes.append("Python project plan created.")

        return plan