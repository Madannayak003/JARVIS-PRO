"""
JARVIS PRO
Builder Integration Test
"""

from __future__ import annotations

from pathlib import Path

from brain.developer.models import (
    ProjectSpecification,
    Language,
    Intent,
)

from brain.developer.planner.planner import ProjectPlanner

from brain.developer.generator.generator_pipeline import GeneratorPipeline

from brain.developer.workspace.workspace_pipeline import WorkspacePipeline
from brain.developer.workspace.models.workspace_request import WorkspaceRequest

from brain.developer.builder.builder_pipeline import BuilderPipeline
from brain.developer.builder.models.build_request import BuildRequest


# --------------------------------------------------
# Specification
# --------------------------------------------------

specification = ProjectSpecification(

    user_request="create python calculator",

    project_name="BuilderTest",

    intent=Intent.CREATE,

    language=Language.PYTHON,

)

# --------------------------------------------------
# Planner
# --------------------------------------------------

planner = ProjectPlanner()

plan = planner.plan(specification)

# --------------------------------------------------
# Generator
# --------------------------------------------------

generator = GeneratorPipeline()

project = generator.generate(plan)

# --------------------------------------------------
# Workspace
# --------------------------------------------------

workspace_request = WorkspaceRequest(

    project=project,

    plan=plan,

    workspace_path=str(
        Path("builder_test")
    ),

)

workspace = WorkspacePipeline().create(

    workspace_request

)

# --------------------------------------------------
# Builder
# --------------------------------------------------

request = BuildRequest(

    project=project,

    plan=plan,

    workspace=workspace,

)

result = BuilderPipeline().build(

    request

)

# --------------------------------------------------
# Results
# --------------------------------------------------

print()

print("=" * 60)

print("BUILDER ENGINE")

print("=" * 60)

print()

print("Success :", result.success)

print()

print("Workspace")

print(result.workspace_path)

print()

print("Steps")

for step in result.steps:

    print(

        f"[{step.success}]",

        step.name,

        "-",

        step.message,

    )

print()

print("Warnings")

for warning in result.warnings:

    print(" -", warning)

print()

print("Errors")

for error in result.errors:

    print(" -", error)

print()

print("Statistics")

print(result.statistics)

print()

print("=" * 60)