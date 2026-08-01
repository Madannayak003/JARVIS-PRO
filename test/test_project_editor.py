from brain.developer.project_finder import ProjectFinder
from brain.developer.project_reader import ProjectReader
from brain.developer.project_editor import ProjectEditor

finder = ProjectFinder()

project = finder.find("calculator")

reader = ProjectReader()

content = reader.read(project.path)

editor = ProjectEditor()

result = editor.edit(

    project_name=project.name,

    language=project.language,

    files=content.files,

    user_request="Add scientific calculator functions."

)

print()

print("Success :", result.success)

print()

print("Returned Files")

print("-" * 60)

for f in result.files:

    print(f)