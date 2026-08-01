from brain.developer.project.technology_detector import TechnologyDetector
from brain.developer.planner.technology_planner import TechnologyPlanner

detector = TechnologyDetector()

planner = TechnologyPlanner()

profile = detector.detect(

    "Create ESP32 RFID Door Lock using MFRC522 Servo LCD WiFi Firebase"

)

plan = planner.build(profile)

print("=" * 60)
print("TECHNOLOGIES")
print("=" * 60)

for item in plan.technologies:
    print(item)

print("\n" + "=" * 60)
print("LIBRARIES")
print("=" * 60)

for item in plan.libraries:
    print(item)

print("\n" + "=" * 60)
print("DEPENDENCIES")
print("=" * 60)

for item in plan.dependencies:
    print(item)

print("\n" + "=" * 60)
print("FOLDERS")
print("=" * 60)

for item in plan.folders:
    print(item)

print("\n" + "=" * 60)
print("FILES")
print("=" * 60)

for item in plan.files:
    print(item)