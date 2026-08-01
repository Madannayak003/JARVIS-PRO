from brain.developer.project_specification import (
    ProjectSpecificationBuilder
)

from brain.developer.specification_organizer import (
    SpecificationOrganizer
)

builder = ProjectSpecificationBuilder()

spec = builder.build(

    "arduino",

    "LED_Blink"

)

files = {

    "main.cpp": "// code",

    "index.html": "<html>",

    "style.css": "",

    "config.h": "// config"

}

organizer = SpecificationOrganizer()

result = organizer.organize(

    spec,

    files

)

print("=" * 60)
print("FILES")
print("=" * 60)

for f in result.files:

    print(f)

print()

print("=" * 60)
print("REMOVED")
print("=" * 60)

print(result.removed)

print()

print("=" * 60)
print("RENAMED")
print("=" * 60)

print(result.renamed)