"""
Project Intelligence Test
"""

from pprint import pprint

from brain.developer.generator.models.generated_file import GeneratedFile
from brain.developer.generator.models.generated_project import GeneratedProject

from brain.developer.project_intelligence.project_intelligence_pipeline import (
    ProjectIntelligencePipeline,
)


def print_section(title):
    print("\n" + "=" * 70)
    print(title.upper())
    print("=" * 70)


def build_project():

    project = GeneratedProject(
        name="Smart Parking",
        language="Python",
        framework="",
    )

    project.add_file(
        GeneratedFile(
            path="main.py",
            language="Python",
            module="Main",
            content="""
import cv2
import numpy
from fastapi import FastAPI

app = FastAPI()

def hello():
    print("Hello")

if __name__ == "__main__":
    hello()
""",
        )
    )

    project.add_file(
        GeneratedFile(
            path="requirements.txt",
            language="Text",
            module="Requirements",
            content="""
fastapi
opencv-python
numpy
""",
        )
    )

    project.add_file(
        GeneratedFile(
            path="README.md",
            language="Markdown",
            module="Docs",
            content="# Smart Parking",
        )
    )

    project.add_file(
        GeneratedFile(
            path="assets/logo.png",
            language="Binary",
            module="Assets",
            content="",
        )
    )

    return project


def main():

    project = build_project()

    pipeline = ProjectIntelligencePipeline()

    result = pipeline.process(project)

    print_section("RESULT")

    print("Success :", result.success)

    print()

    intelligence = result.intelligence

    print_section("LANGUAGE")
    print(intelligence.language)

    print_section("FRAMEWORK")
    print(intelligence.framework)

    print_section("RUNTIME")
    print(intelligence.runtime)

    print_section("DEPENDENCIES")
    pprint(intelligence.dependencies)

    print_section("ENTRY POINT")
    pprint(intelligence.entry_point)

    print_section("SOURCE FILES")
    pprint(intelligence.source_files)

    print_section("ASSET FILES")
    pprint(intelligence.asset_files)

    print_section("CONFIGURATION FILES")
    pprint(intelligence.configuration_files)

    print_section("IMPORTANT FILES")
    pprint(intelligence.important_files)

    print_section("WARNINGS")
    pprint(result.warnings)

    print_section("ERRORS")
    pprint(result.errors)

    print_section("METADATA")
    pprint(result.metadata)


if __name__ == "__main__":
    main()