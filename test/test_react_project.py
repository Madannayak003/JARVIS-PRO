from brain.developer.generator.models.generated_file import GeneratedFile
from brain.developer.generator.models.generated_project import GeneratedProject

from brain.developer.project_intelligence.project_intelligence_pipeline import (
    ProjectIntelligencePipeline,
)


def main():

    project = GeneratedProject(
        name="React Dashboard",
        language="JavaScript",
        framework="",
    )

    project.add_file(
        GeneratedFile(
            path="src/main.jsx",
            language="JavaScript",
            module="Main",
            content="""
import React from "react"
import ReactDOM from "react-dom"

ReactDOM.createRoot(
    document.getElementById("root")
)
""",
        )
    )

    project.add_file(
        GeneratedFile(
            path="package.json",
            language="JSON",
            module="",
            content="""
{
    "dependencies": {
        "react":"18",
        "react-dom":"18"
    }
}
""",
        )
    )

    project.add_file(
        GeneratedFile(
            path="public/logo.png",
            language="Binary",
            module="",
            content="",
        )
    )

    pipeline = ProjectIntelligencePipeline()

    result = pipeline.process(project)

    print("\n===== REACT PROJECT =====")
    print(result.intelligence)


if __name__ == "__main__":
    main()