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

from ai.memory_intent import handle

tests = [

    "Forget my email",

    "Delete my phone number",

    "Forget my college",

    "Forget my laptop",

    "Forget everything about education",

    "Forget everything"

]

for t in tests:

    print("-" * 60)

    print("USER :", t)

    print(handle(t))