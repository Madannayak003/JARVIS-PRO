from brain.developer.developer_workspace import DeveloperWorkspace

workspace = DeveloperWorkspace()

tests = [

    ("python", "calculator"),

    ("html", "portfolio"),

    ("arduino", "traffic_light"),

    ("javascript", "dashboard"),

    ("python", "calculator"),   # duplicate test

]

for language, project in tests:

    result = workspace.create_project(

        language,

        project

    )

    print()

    print("Project :", result.project_path)

    print("Main File:", result.file_path)