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

from ai.memory_preference import extract


tests = [

    "I like Python.",

    "I love coffee.",

    "I prefer dark mode.",

    "I usually use VS Code.",

    "I always use Chrome.",

    "Today is hot.",

    "Open Chrome."

]


for t in tests:

    print("-" * 60)

    print(t)

    print(extract(t))