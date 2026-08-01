from brain.developer.project_finder import ProjectFinder
from brain.developer.project_reader import ProjectReader

finder = ProjectFinder()

project = finder.find("calculator")

if not project.found:

    print("Project not found")

    raise SystemExit

reader = ProjectReader()

result = reader.read(project.path)

print("=" * 60)
print("PROJECT")
print("=" * 60)

print(project.path)

print()

print("=" * 60)
print("FILES")
print("=" * 60)

for filename, content in result.files.items():

    print(filename)

    print("-" * 40)

    print(content[:300])

    print()

print("=" * 60)

print("Read :", result.total_read)

print("Skipped :", len(result.skipped))

if result.skipped:

    print()

    print("Skipped Files")

    for file in result.skipped:

        print(file)