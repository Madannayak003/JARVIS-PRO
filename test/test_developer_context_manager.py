from brain.developer.developer_workflow import DeveloperWorkflow

workflow = DeveloperWorkflow()

request = workflow.prepare_request(
    "update calculator"
)

context = workflow.context_manager.build(request)

print("=" * 60)
print("DEVELOPER CONTEXT")
print("=" * 60)

print("Project :", context.project_name)
print("Language:", context.language)
print("Files   :", context.total_files)
print("Chars   :", context.total_characters)

print()
print("=" * 60)
print("PROMPT")
print("=" * 60)

print(context.prompt)