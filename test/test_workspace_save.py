from brain.developer.developer_workspace import DeveloperWorkspace

workspace = DeveloperWorkspace()

result = workspace.create_project(

    "python",

    "calculator"

)

sample_code = """

print("Hello from JARVIS")

"""

workspace.save_code(

    result.file_path,

    sample_code

)

print()

print(workspace.read_file(result.file_path))