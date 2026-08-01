from brain.developer.project_finder import ProjectFinder
from brain.developer.project_reader import ProjectReader
from brain.developer.project_context import ProjectContextBuilder

finder = ProjectFinder()

project = finder.find("calculator")

if not project.found:

    print("Project not found")

    raise SystemExit

reader = ProjectReader()

content = reader.read(project.path)

builder = ProjectContextBuilder()

context = builder.build(

    project_name=project.name,

    language=project.language,

    user_request="Add scientific calculator features.",

    files=content.files

)

print("=" * 70)

print(context.prompt[:4000])

print()

print("=" * 70)

print("Files      :", context.total_files)

print("Characters :", context.total_characters)