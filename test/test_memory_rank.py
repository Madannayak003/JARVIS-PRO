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
from ai.memory_rank import rank


print("-" * 60)

for memory in rank(list_all()):

    print(

        memory.key,

        memory.value,

        memory.importance,

        memory.use_count

    )