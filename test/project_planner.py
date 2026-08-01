from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.planner.project_planner import ProjectPlannerV2

detector = TechnologyDetector()

planner = TechnologyPlanner()

spec_builder = ProjectSpecificationBuilder()

profile = detector.detect(

    "Create ESP32 RFID Door Lock using MFRC522 Servo LCD WiFi Firebase"

)

tech_plan = planner.build(profile)

spec = spec_builder.build(

    "esp32",

    "RFID_Door_Lock"

)

project = ProjectPlannerV2().build(

    spec,

    tech_plan

)

print("=" * 60)
print("PROJECT")
print("=" * 60)

print(project.project_name)
print(project.language)
print(project.workspace)
print(project.main_file)

print("\nFILES")

for f in project.files:
    print("-", f)

print("\nLIBRARIES")

for lib in project.libraries:
    print("-", lib)