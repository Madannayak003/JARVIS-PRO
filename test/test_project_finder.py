from brain.developer.project_finder import ProjectFinder

finder = ProjectFinder()

print("=" * 60)
print("ALL PROJECTS")
print("=" * 60)

for project in finder.list_projects():

    print(project.language, "->", project.name)

print()

print("=" * 60)
print("SEARCH")
print("=" * 60)

tests = [

    "calculator",

    "login",

    "portfolio",

    "unknown"

]

for name in tests:

    result = finder.find(name)

    print()

    print(name)

    print(result)