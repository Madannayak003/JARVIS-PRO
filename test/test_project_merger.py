from pathlib import Path

from brain.developer.project_merger import ProjectMerger

merger = ProjectMerger()

files = {

    "main.py": "print('Updated')",

    "scientific.py": "print('Scientific Calculator')",

    "folder/test.py": "print('Nested File')"

}

result = merger.merge(

    Path("workspace/Python/Calculator"),

    files

)

print()

print("UPDATED")

for f in result.updated:

    print(f)

print()

print("CREATED")

for f in result.created:

    print(f)