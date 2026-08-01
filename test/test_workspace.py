# """
# JARVIS PRO
# Phase 4 - Workspace Engine Test
# """

# from __future__ import annotations

# from brain.developer.analysis.analyzer import ProjectAnalyzer

# from brain.developer.planner.models import ProjectPlan
# from brain.developer.planner.planner_pipeline import PlannerPipeline

# from brain.developer.generator.generator_pipeline import GeneratorPipeline
# from brain.developer.generator.models.generation_request import (
#     GenerationRequest,
# )

# from brain.developer.workspace.workspace_pipeline import WorkspacePipeline
# from brain.developer.workspace.models.workspace_request import (
#     WorkspaceRequest,
# )


# def main():

#     print("=" * 80)
#     print("JARVIS PRO - PHASE 4 WORKSPACE TEST")
#     print("=" * 80)

#     # -------------------------------------------------
#     # User Request
#     # -------------------------------------------------

#     user_request = (
#         "Create an ESP32 weather station using "
#         "WiFi Firebase MQTT"
#     )

#     # -------------------------------------------------
#     # Analyzer
#     # -------------------------------------------------

#     analyzer = ProjectAnalyzer()

#     specification = analyzer.analyze(user_request)

#     # -------------------------------------------------
#     # Planner
#     # -------------------------------------------------

#     project_plan = ProjectPlan(
#         specification=specification,
#     )

#     planner = PlannerPipeline()

#     planner.run(project_plan)

#     # -------------------------------------------------
#     # Generator
#     # -------------------------------------------------

#     generator = GeneratorPipeline()

#     generation_request = GenerationRequest(
#         project=project_plan,
#         model="jarvis",
#     )

#     generation_result = generator.generate(
#         generation_request
#     )

#     if not generation_result.success:

#         print("\nGenerator Failed\n")

#         for error in generation_result.errors:
#             print("-", error)

#         return

#     # -------------------------------------------------
#     # Workspace
#     # -------------------------------------------------

#     workspace = WorkspacePipeline()

#     workspace_request = WorkspaceRequest(
#         project=generation_result.project,
#         plan=project_plan,
#         workspace_root="workspace",
#         overwrite=True,
#     )

#     workspace_result = workspace.build(
#         workspace_request
#     )

#     # -------------------------------------------------
#     # Results
#     # -------------------------------------------------

#     print()

#     print("Success :", workspace_result.success)

#     print("Workspace :", workspace_result.workspace_path)

#     print()

#     print("Written Files")

#     print("-" * 80)

#     for file in workspace_result.written_files:

#         print(file.path)

#     print()

#     print("Warnings :", len(workspace_result.warnings))

#     for warning in workspace_result.warnings:
#         print("-", warning)

#     print()

#     print("Errors :", len(workspace_result.errors))

#     for error in workspace_result.errors:
#         print("-", error)

#     print()

#     if workspace_result.success:
#         print("=" * 80)
#         print("✅ Phase 4 Workspace PASSED")
#         print("=" * 80)
#     else:
#         print("=" * 80)
#         print("❌ Phase 4 Workspace FAILED")
#         print("=" * 80)


# if __name__ == "__main__":
#     main()

from __future__ import annotations

import shutil
from pathlib import Path

from brain.developer.generator.models.generated_file import GeneratedFile
from brain.developer.generator.models.generated_project import GeneratedProject

from brain.developer.workspace.models.workspace_request import WorkspaceRequest
from brain.developer.workspace.workspace_pipeline import WorkspacePipeline

from brain.developer.planner.models.project_plan import ProjectPlan
from brain.developer.models import (
    ProjectSpecification,
    Runtime,
)
from brain.developer.models.enums import (
    Workspace,
    Language,
)


def create_request() -> WorkspaceRequest:

    project = GeneratedProject(
        name="WorkspaceTest",
        language="Python",
        framework="",
    )

    project.add_file(
        GeneratedFile(
            path="main.py",
            content='print("Hello Workspace")',
            language="Python",
            module="core",
        )
    )

    project.add_file(
        GeneratedFile(
            path="src/utils.py",
            content="# Utilities",
            language="Python",
            module="utils",
        )
    )

    specification = ProjectSpecification(
        project_name="WorkspaceTest",
        workspace=Workspace.PYTHON,
        language=Language.PYTHON,
    )

    plan = ProjectPlan(
        specification=specification,
    )

    workspace_root = Path("workspace_test")

    if workspace_root.exists():
        shutil.rmtree(workspace_root)

    return WorkspaceRequest(
        project=project,
        plan=plan,
        workspace_root=str(workspace_root),
        overwrite=True,
    )


def main():

    request = create_request()

    pipeline = WorkspacePipeline()

    result = pipeline.build(request)

    print()

    print("=" * 60)
    print("WORKSPACE TEST")
    print("=" * 60)

    print("Success :", result.success)
    print("Workspace :", result.workspace_path)

    print()

    print("Files")

    for file in result.written_files:
        print(" ", file.path)

    print()

    print("Warnings :", result.warnings)
    print("Errors   :", result.errors)

    print("=" * 60)


if __name__ == "__main__":
    main()

# from brain.developer.generator.models.generated_file import GeneratedFile

# print(GeneratedFile.__module__)

# f = GeneratedFile(
#     path="src/main.py",
#     content="",
#     language="Python",
#     module="core",
# )

# print(f.directory)