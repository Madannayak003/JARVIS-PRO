from brain.developer.generator.models.generated_file import GeneratedFile
from brain.developer.generator.models.generated_project import GeneratedProject

from brain.developer.project_intelligence.project_intelligence_pipeline import (
    ProjectIntelligencePipeline,
)


def main():

    project = GeneratedProject(
        name="FastAPI Project",
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

if __name__ == "__main__":
    print("Running")
""",
        )
    )

    project.add_file(
        GeneratedFile(
            path="requirements.txt",
            language="Text",
            module="",
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
            module="",
            content="# Demo",
        )
    )

    pipeline = ProjectIntelligencePipeline()

    result = pipeline.process(project)

    print("\n===== PYTHON PROJECT =====")
    print(result.intelligence)


if __name__ == "__main__":
    main()