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

from ai.memory_profile import profile_summary
from ai.memory_profile import ai_profile


print(profile_summary())

print("\n")

print("=" * 50)

print(ai_profile())