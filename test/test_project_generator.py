from brain.developer.project.project_specification import ProjectSpecificationBuilder
from brain.developer.project.technology_detector import TechnologyDetector

from brain.developer.planner.technology_planner import TechnologyPlanner
from brain.developer.planner.project_planner import ProjectPlanner
from brain.developer.planner.project_architecture_builder import ProjectArchitectureBuilder
from brain.developer.planner.interface_builder import InterfaceBuilder
from brain.developer.planner.project_flow_builder import ProjectFlowBuilder
from brain.developer.planner.generation_orchestrator import GenerationOrchestrator

from brain.developer.engine.project_generator import ProjectGenerator


# ==========================================================
# Build Project Information
# ==========================================================

spec = ProjectSpecificationBuilder().build(
    "esp32",
    "RFID_Door_Lock"
)

profile = TechnologyDetector().detect(
    "Create ESP32 RFID Door Lock using MFRC522 Servo LCD WiFi Firebase"
)

tech = TechnologyPlanner().build(profile)

plan = ProjectPlanner().build(
    spec,
    tech
)

architecture = ProjectArchitectureBuilder().build(
    plan
)

interfaces = InterfaceBuilder().build(
    architecture
)

flow = ProjectFlowBuilder().build(
    interfaces
)

generation = GenerationOrchestrator().build(
    architecture
)

generator = ProjectGenerator()

# ==========================================================
# Generate Project
# ==========================================================

result = generator.generate(

    specification=spec,

    technology=tech,

    plan=plan,

    architecture=architecture,

    interfaces=interfaces,

    flow=flow,

    generation_plan=generation

)

# ==========================================================
# Results
# ==========================================================

print("=" * 60)
print("SUCCESS :", result.success)
print("MODULES :", result.modules_generated)
print("FILES   :", len(result.generated_files))

if result.validation:

    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)

    print("Success :", result.validation.success)
    print("Missing :", result.validation.missing)
    print("Unexpected :", result.validation.unexpected)
    print("Empty :", result.validation.empty_files)

print("=" * 60)
print("GENERATED FILES")
print("=" * 60)

for filename in sorted(result.generated_files.keys()):
    print(filename)

if not result.success:

    print("=" * 60)
    print("FAILED MODULE :", result.failed_module)
    print("ERROR :", result.error)
    
    