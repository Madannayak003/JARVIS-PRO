"""
JARVIS PRO
Phase 5 - Project Memory Test
"""

from __future__ import annotations

from pathlib import Path

from brain.developer.analysis.analyzer import ProjectAnalyzer

from brain.developer.planner.models import ProjectPlan
from brain.developer.planner.planner_pipeline import PlannerPipeline

from brain.developer.generator.generator_pipeline import GeneratorPipeline
from brain.developer.generator.models.generation_request import (
    GenerationRequest,
)

from brain.developer.workspace.workspace_pipeline import WorkspacePipeline
from brain.developer.workspace.models.workspace_request import (
    WorkspaceRequest,
)

from brain.developer.project_memory.project_pipeline import (
    ProjectPipeline,
)

from brain.developer.project_memory.project_memory import (
    ProjectMemory,
)


def main():

    print("=" * 80)
    print("JARVIS PRO - PHASE 5 PROJECT MEMORY TEST")
    print("=" * 80)

    # -------------------------------------------------
    # User Request
    # -------------------------------------------------

    user_request = (
        "Create an ESP32 weather station "
        "using WiFi Firebase MQTT"
    )

    # -------------------------------------------------
    # Analyzer
    # -------------------------------------------------

    analyzer = ProjectAnalyzer()

    specification = analyzer.analyze(user_request)

    # -------------------------------------------------
    # Planner
    # -------------------------------------------------

    project_plan = ProjectPlan(
        specification=specification,
    )

    planner = PlannerPipeline()

    planner.run(project_plan)

    # -------------------------------------------------
    # Generator
    # -------------------------------------------------

    generator = GeneratorPipeline()

    generation_request = GenerationRequest(
        project=project_plan,
        model="jarvis",
    )

    generation_result = generator.generate(
        generation_request
    )

    if not generation_result.success:

        print("\nGenerator Failed\n")

        for error in generation_result.errors:
            print("-", error)

        return

    # -------------------------------------------------
    # Workspace
    # -------------------------------------------------

    workspace = WorkspacePipeline()

    workspace_request = WorkspaceRequest(
        project=generation_result.project,
        plan=project_plan,
        workspace_root="workspace",
        overwrite=True,
    )

    workspace_result = workspace.build(
        workspace_request
    )

    if not workspace_result.success:

        print("\nWorkspace Failed\n")

        return

    # -------------------------------------------------
    # Project Memory
    # -------------------------------------------------

    project_pipeline = ProjectPipeline(
        workspace_root="workspace",
    )

    project_info = project_pipeline.register(
        workspace_result,
        project_plan,
    )

    print("\nProject Registered")

    print("-" * 80)

    print("Name       :", project_info.name)
    print("Workspace  :", project_info.workspace)
    print("Language   :", project_info.language)
    print("Framework  :", project_info.framework)
    print("Board      :", project_info.board)

    # -------------------------------------------------
    # Registry Test
    # -------------------------------------------------

    memory = ProjectMemory("workspace")

    index = memory.projects()

    print("\nRegistered Projects")

    print("-" * 80)

    for project in index.projects:

        print(project.name)

    # -------------------------------------------------
    # Search Test
    # -------------------------------------------------

    result = memory.search("esp32")

    print("\nSearch Result")

    print("-" * 80)

    if result:

        print("Found :", result.name)

    else:

        print("No Project Found")

    # -------------------------------------------------
    # Load Test
    # -------------------------------------------------

    if result:

        loaded = memory.load(
            Path(result.path)
        )

        print("\nLoaded Project")

        print("-" * 80)

        print("Name      :", loaded.name)
        print("Workspace :", loaded.workspace)
        print("Language  :", loaded.language)
        print("Framework :", loaded.framework)
        print("Board     :", loaded.board)

    print()

    print("=" * 80)
    print("✅ Phase 5 Project Memory PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()