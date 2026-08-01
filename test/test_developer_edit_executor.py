from brain.developer.developer_workflow import DeveloperWorkflow
from brain.developer.developer_edit_executor import DeveloperEditExecutor

workflow = DeveloperWorkflow()

request = workflow.prepare_request(

    "update calculator"

)

executor = DeveloperEditExecutor()

result = executor.execute(

    request

)

print("=" * 60)
print("EXECUTOR RESULT")
print("=" * 60)

print(result)

print()

print("=" * 60)
print("AI")
print("=" * 60)

print("Success :", result.ai_success)

print("Characters :", len(result.raw_response))

print()

print("=" * 60)
print("PARSER")
print("=" * 60)

print("Files :", result.parsed_files)

if result.parsed:

    print()

    for file in result.parsed.files:

        print(file)

print()

print(result.raw_response[:500])

print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)

print(result.summary_text)
