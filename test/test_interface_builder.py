from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlannerV2
from brain.developer.planner.project_architecture_builder import ProjectArchitectureBuilder
from brain.developer.planner.interface_builder import InterfaceBuilder

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

interfaces = InterfaceBuilder().build(
    architecture
)

for interface in interfaces.interfaces:

    print("=" * 60)
    print(interface.module)
    print("=" * 60)

    print("Header :", interface.header)
    print("Source :", interface.source)

    print("\nFunctions")

    for func in interface.functions:
        print(" ", func)

    print()