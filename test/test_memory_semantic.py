import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from ai.memory_semantic import search

tests = [

    "Who am I?",

    "Where am I studying?",

    "Which university?",

    "What laptop do I use?",

    "Which operating system?",

    "What is my email?",

    "What is my phone number?",

    "Which project?",

    "Which programming language?"

]

for question in tests:

    print("-" * 60)

    print(question)

    memory = search(question)

    if memory:

        print(

            memory.key,

            "=",

            memory.value

        )

    else:

        print("No match")