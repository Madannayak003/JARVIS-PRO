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

from ai.memory_confidence import confidence


tests = [

    ("name", "Madan R"),

    ("name", "Madan"),

    ("college", "VVCE Mysore"),

    ("os", "Windows 11"),

    ("favorite_language", "Python")

]


for key, value in tests:

    print("-" * 60)

    print(key, "=", value)

    print(

        confidence(

            key,

            value

        )

    )