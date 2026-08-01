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

from ai.memory_store import list_all

for m in list_all():
    print(m.key, m.value, m.category)