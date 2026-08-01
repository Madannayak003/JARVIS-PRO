"""
JARVIS PRO
Generator Integration Test

Tests:
Analysis
    ↓
Planner
    ↓
Generator
"""

from brain.developer.analysis.analyzer import ProjectAnalyzer
from brain.developer.planner.planner import ProjectPlanner

from brain.developer.generator.generator_pipeline import GeneratorPipeline
from brain.developer.generator.models.generation_request import GenerationRequest


# -------------------------------------------------
# Build Project Plan
# -------------------------------------------------

analyzer = ProjectAnalyzer()
planner = ProjectPlanner()

spec = analyzer.analyze(
    "build esp32 weather station using wifi mqtt firebase"
)

plan = planner.plan(spec)


# -------------------------------------------------
# Run Generator
# -------------------------------------------------

generator = GeneratorPipeline()

request = GenerationRequest(
    project=plan,
    model="jarvis",
)

result = generator.generate(request)


# -------------------------------------------------
# Print Result
# -------------------------------------------------

print("=" * 80)
print("JARVIS PRO - PHASE 3 GENERATOR TEST")
print("=" * 80)

print(f"\nSuccess : {result.success}")

print(f"Warnings : {len(result.warnings)}")
for warning in result.warnings:
    print(" -", warning)

print(f"\nErrors : {len(result.errors)}")
for error in result.errors:
    print(" -", error)

print("\nGenerated Files")
print("-" * 80)

if not result.project.files:

    print("No files generated.")

else:

    for generated_file in result.project.files:

        print(f"\nPath     : {generated_file.path}")
        print(f"Language : {generated_file.language}")
        print(f"Module   : {generated_file.module}")

        print("\nContent Preview")
        print("-" * 40)

        preview = generated_file.content[:300]

        print(preview)

        if len(generated_file.content) > 300:
            print("...")

print("\n" + "=" * 80)

if result.success:
    print("✅ Phase 3 Generator PASSED")
else:
    print("❌ Phase 3 Generator FAILED")

print("=" * 80)