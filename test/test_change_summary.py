from pathlib import Path

from brain.developer.workflow.change_summary import ChangeSummary

summary = ChangeSummary()

result = summary.build(

    updated=[

        Path("workspace/Python/Calculator/main.py"),

        Path("workspace/Python/Calculator/README.md")

    ],

    created=[

        Path("workspace/Python/Calculator/scientific.py"),

        Path("workspace/Python/Calculator/utils.py")

    ],

    deleted=[]

)

print(result.report)