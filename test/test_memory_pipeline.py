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

from ai.memory_pipeline import learn

tests = [

    "My name is Madan R",

    "I use Windows 11.",

    "My laptop is HP.",

    "My email is madan@example.com",

    "Today is hot."

]

for t in tests:

    print("-" * 60)

    print("USER :", t)

    print(learn(t))