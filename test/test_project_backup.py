from brain.developer.project_finder import ProjectFinder
from brain.developer.project_backup import ProjectBackup

finder = ProjectFinder()

project = finder.find("calculator")

if not project.found:

    print("Project not found")

    raise SystemExit

backup = ProjectBackup()

result = backup.create(

    project.path

)

print()

print("=" * 60)

print("SUCCESS")

print("=" * 60)

print(result.success)

print()

print("=" * 60)

print("BACKUP")

print("=" * 60)

print(result.backup_path)