from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlannerV2
from brain.developer.builders.builders.readme_builder import ReadmeBuilder

spec = ProjectSpecificationBuilder().build(
    "esp32",
    "RFID_Door_Lock"
)

profile = TechnologyDetector().detect(
    "Create ESP32 RFID Door Lock using MFRC522 Servo LCD WiFi Firebase"
)

technology = TechnologyPlanner().build(profile)

plan = ProjectPlannerV2().build(
    spec,
    technology
)

builder = ReadmeBuilder()

result = builder.build(

    spec,

    technology,

    plan

)

print(result.content)