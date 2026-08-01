from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlannerV2
from brain.developer.planner.project_architecture_builder import ProjectArchitectureBuilder

spec = ProjectSpecificationBuilder().build(
    "esp32",
    "RFID_Door_Lock"
)

profile = TechnologyDetector().detect(
    "Create ESP32 RFID Door Lock using MFRC522 Servo LCD WiFi Firebase"
)

tech = TechnologyPlanner().build(profile)

plan = ProjectPlannerV2().build(spec, tech)

architecture = ProjectArchitectureBuilder().build(plan)

print("=" * 60)
print("PROJECT")
print("=" * 60)
print(architecture.project_name)

print("Main :", architecture.main_file)
print("Config :", architecture.config_file)
print("Readme :", architecture.readme_file)

print()

for module in architecture.modules:

    print("=" * 60)
    print(module.name)
    print("=" * 60)

    print("Purpose:")
    print(module.purpose)

    print("\nLibraries:")

    for lib in module.libraries:
        print(" ", lib)

    print("\nFiles:")

    for file in module.files:
        print(" ", file)

    print()