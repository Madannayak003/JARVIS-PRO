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

from ai.memory_ai import extract_memory

tests = [

    "My laptop is HP.",

    "I use Windows 11.",

    "I love Python.",

    "My email is madan@example.com",

    "Today is very hot.",

    "Can you open Chrome?",

    "I am studying at VVCE Mysore."
]

for text in tests:

    print("-" * 60)

    print("USER :", text)

    print(extract_memory(text))