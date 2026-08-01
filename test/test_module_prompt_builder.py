from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlannerV2
from brain.developer.planner.project_architecture_builder import ProjectArchitectureBuilder
from brain.developer.planner.module_prompt_builder import ModulePromptBuilder

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

builder = ModulePromptBuilder()

for module in architecture.modules:

    result = builder.build(

        project_name=architecture.project_name,

        language=plan.language,

        board=plan.board,

        module=module

    )

    print("=" * 70)
    print(result.module)
    print("=" * 70)
    print(result.prompt)
    print()