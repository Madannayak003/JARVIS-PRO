from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlannerV2
from brain.developer.planner.project_architecture_builder import ProjectArchitectureBuilder
from brain.developer.planner.interface_builder import InterfaceBuilder
from brain.developer.planner.project_flow_builder import ProjectFlowBuilder
from brain.developer.planner.generation_orchestrator import GenerationOrchestrator
from brain.developer.planner.generation_context_builder import GenerationContextBuilder
from brain.developer.engine.module_generator import ModuleGenerator

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

generation = GenerationOrchestrator().build(architecture)

builder = GenerationContextBuilder()

generator = ModuleGenerator()

# Generate only RFID module

rfid_step = next(
    s for s in generation.steps
    if s.name == "rfid"
)

context = builder.build(
    rfid_step,
    spec,
    architecture,
    interfaces,
    flow
)

result = generator.generate(context)

print("=" * 60)
print("Success :", result.success)
print("Module  :", result.module)

if result.success:

    print("Files")

    for name in result.files:

        print(" ", name)

else:

    print(result.error)