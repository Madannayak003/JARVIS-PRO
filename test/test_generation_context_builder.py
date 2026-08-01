from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlannerV2
from brain.developer.planner.project_architecture_builder import ProjectArchitectureBuilder
from brain.developer.planner.interface_builder import InterfaceBuilder
from brain.developer.planner.project_flow_builder import ProjectFlowBuilder
from brain.developer.planner.generation_orchestrator import GenerationOrchestrator
from brain.developer.planner.generation_context_builder import GenerationContextBuilder

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

orchestrator = GenerationOrchestrator()

generation = orchestrator.build(architecture)

builder = GenerationContextBuilder()

for step in generation.steps:

    if step.name in ("config", "main"):
        continue

    context = builder.build(
        step,
        spec,
        architecture,
        interfaces,
        flow
    )

    print("=" * 70)
    print(context.module.upper())
    print("=" * 70)

    print("Files:")
    for f in context.files:
        print(" ", f)

    print("\nLibraries:")
    for lib in context.libraries:
        print(" ", lib)

    print("\nInterfaces:")
    for fn in context.interfaces:
        print(" ", fn)

    print("\nSetup:")
    for fn in context.setup:
        print(" ", fn)

    print("\nLoop:")
    for fn in context.loop:
        print(" ", fn)

    print("\nPrompt Preview:")
    print(context.prompt[:250], "...")
    print()