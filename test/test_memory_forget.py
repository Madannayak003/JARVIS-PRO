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
from ai.memory_forget import (
    forget_key,
    forget_category,
    forget_all
)


print("Before")

for m in list_all():

    print(m.key, "=", m.value)

print("-" * 50)

print(

    forget_key("os")

)

print("-" * 50)

print("After")

for m in list_all():

    print(m.key, "=", m.value)