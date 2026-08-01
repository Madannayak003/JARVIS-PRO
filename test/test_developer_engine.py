from brain.developer.developer_engine import DeveloperEngine

response = """
```python
# calculator.py

print("Calculator")

```

README.md

Python Calculator

"""

engine = DeveloperEngine()

project = engine.save_project(
    language="python",

    project_type="calculator",

    response=response
)

print()

print("Success :", project.success)

print("Folder :", project.project_path)

print("Main :", project.main_file)

print()

print("Files")

for file in project.files:
    
    print(file)
