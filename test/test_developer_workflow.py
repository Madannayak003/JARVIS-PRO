from brain.developer.developer_workflow import DeveloperWorkflow

workflow = DeveloperWorkflow()

tests = [

    "create python calculator",

    "update calculator",

    "edit calculator",

    "open calculator",

    "continue calculator",

    "create html portfolio"

]

for command in tests:

    print("=" * 60)

    print(command)

    print()

    result = workflow.handle(command)

    print(result)

    print("Action :", result.action)

    print("Found  :", result.project_found)

    print("Project:", result.project_name)

    print("Path   :", result.project_path)
    
    print("Merged :", result.merged)

    print()

    if result.summary_text:

        print(result.summary_text)
    
    request = workflow.prepare_request("update calculator")

    if request.project_content:

        print("=" * 60)
        print("FILES")
        print("=" * 60)

        print("Success :", request.project_content.success)
        print("Read    :", request.project_content.total_read)
        print("Skipped :", len(request.project_content.skipped))

        print()

        for name in request.project_content.files:

            print(name)
            
    if request.project_context:

        print("=" * 60)
        print("PROJECT CONTEXT")
        print("=" * 60)

        print("Files      :", request.project_context.total_files)

        print("Characters :", request.project_context.total_characters)

        print()

        print(request.project_context.prompt[:1000])
        
        print("Backup :", result.backup_path)        