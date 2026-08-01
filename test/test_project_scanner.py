from brain.developer.project_finder import ProjectFinder
from brain.developer.project_scanner import ProjectScanner

finder = ProjectFinder()

project = finder.find("calculator")

if not project.found:

    print("Project not found")

    quit()

scanner = ProjectScanner()

result = scanner.scan(project.path)

print("=" * 60)
print("PROJECT")
print("=" * 60)

print(result.root)

print()

print("=" * 60)
print("FOLDERS")
print("=" * 60)

for folder in result.folders:

    print(folder)

print()

print("=" * 60)
print("FILES")
print("=" * 60)

for file in result.files:

    print(file)

print()

print("=" * 60)

print("Folders :", result.total_folders)

print("Files   :", result.total_files)