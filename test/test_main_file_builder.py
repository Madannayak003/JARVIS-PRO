from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlannerV2
from brain.developer.planner.project_architecture_builder import ProjectArchitectureBuilder
from brain.developer.planner.interface_builder import InterfaceBuilder
from brain.developer.planner.project_flow_builder import ProjectFlowBuilder
from brain.developer.engine.main_file_builder import MainFileBuilder

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

interfaces = InterfaceBuilder().build(architecture)

flow = ProjectFlowBuilder().build(interfaces)

builder = MainFileBuilder()

result = builder.build(

    spec,

    interfaces,

    flow

)

print("=" * 60)
print(result.filename)
print("=" * 60)
print(result.content)