from ai.memory import init_memory
from ai.memory_store import remember

from ai.prompt_builder import build_prompt

init_memory()

remember(
    "name",
    "Madan R",
    keywords="name,user,identity"
)

remember(
    "college",
    "VVCE Mysore",
    keywords="college,education"
)

print(

    build_prompt(
        "What is my name?"
    )

)