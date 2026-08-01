from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlannerV2
from brain.developer.planner.project_architecture_builder import ProjectArchitectureBuilder
from brain.developer.planner.generation_orchestrator import GenerationOrchestrator

spec = ProjectSpecificationBuilder().build(
    "esp32",
    "RFID_Door_Lock"
)

profile = TechnologyDetector().detect(
    "Create ESP32 RFID Door Lock using MFRC522 Servo LCD WiFi Firebase"
)

tech = TechnologyPlanner().build(profile)

plan = ProjectPlannerV2().build(
    spec,
    tech
)

architecture = ProjectArchitectureBuilder().build(
    plan
)

generation = GenerationOrchestrator().build(
    architecture
)

print("=" * 60)

for step in generation.steps:

    print(f"{step.priority:4}  {step.name}")

    for file in step.files:
        print("      ", file)

    print()