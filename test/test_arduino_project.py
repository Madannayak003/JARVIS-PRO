from brain.developer.generator.models.generated_file import GeneratedFile
from brain.developer.generator.models.generated_project import GeneratedProject
from brain.developer.project_intelligence.project_intelligence_pipeline import (
    ProjectIntelligencePipeline,
)


def main():

    project = GeneratedProject(
        name="Smart Parking",
        language="Arduino",
        framework="",
    )

    project.add_file(
        GeneratedFile(
            path="SmartParking.ino",
            language="Arduino",
            module="Main",
            content="""
#include <WiFi.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

void setup(){

}

void loop(){

}
""",
        )
    )

    project.add_file(
        GeneratedFile(
            path="platformio.ini",
            language="Text",
            module="",
            content="""
[env:esp32]
platform = espressif32
framework = arduino
""",
        )
    )

    project.add_file(
        GeneratedFile(
            path="README.md",
            language="Markdown",
            module="",
            content="# Smart Parking",
        )
    )

    pipeline = ProjectIntelligencePipeline()

    result = pipeline.process(project)

    print("\n===== ARDUINO PROJECT =====")
    print(result.intelligence)


if __name__ == "__main__":
    main()