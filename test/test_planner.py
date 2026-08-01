from brain.developer.analysis.analyzer import ProjectAnalyzer
from brain.developer.planner.planner import ProjectPlanner

analyzer = ProjectAnalyzer()
planner = ProjectPlanner()

spec = analyzer.analyze(
    "build esp32 weather station using wifi mqtt firebase"
)

plan = planner.plan(spec)

print("Layout:", plan.layout.name)

print("\nCapabilities")

for capability in plan.capabilities:
    print(
        capability.priority,
        capability.name,
        "-",
        capability.description,
    )
    
print()

print("Dependencies")

for dependency in plan.dependencies:

    print(dependency.name)
    
print()

print("Modules")

for module in plan.modules:

    print(module.name)  
    
print()

print("Files")

for file in plan.files:

    print(file.path)
    
print()
print("Validation")

if not plan.validation.issues:

    print("No issues")

else:

    for issue in plan.validation.issues:

        print(
            f"[{issue.severity.value}] "
            f"{issue.code} : "
            f"{issue.message}"
        )  
    