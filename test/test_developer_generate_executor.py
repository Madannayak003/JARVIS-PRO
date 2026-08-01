from brain.developer.developer_generate_executor import (
    DeveloperGenerateExecutor
)

from brain.developer.developer_workflow import DeveloperWorkflow

executor = DeveloperGenerateExecutor()

workflow = DeveloperWorkflow()

request = workflow.prepare_request(

    "create python calculator"

)

result = executor.execute(

    request

)

print("=" * 60)
print("GENERATE EXECUTOR")
print("=" * 60)

print(result)