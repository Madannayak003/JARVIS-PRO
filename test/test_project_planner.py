from brain.developer.project.project_specification import ProjectSpecificationBuilder
from archive.project_planner_legacy import ProjectPlanner

spec = ProjectSpecificationBuilder().build(
    "arduino",
    "RFID_Door_Lock"
)

plan = ProjectPlanner().build(spec)

print("=" * 60)
print(plan.language)
print(plan.project_name)
print()

for f in plan.files:
    print(f.name, "-", f.description)