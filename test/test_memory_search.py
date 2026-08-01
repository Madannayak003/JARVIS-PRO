from ai.memory import init_memory
from ai.memory_store import remember
from ai.memory_search import search

init_memory()

remember(
    "name",
    "Madan R",
    keywords="name,user,identity"
)

remember(
    "college",
    "NIE Mysore",
    keywords="college,education"
)

remember(
    "project",
    "JARVIS PRO",
    keywords="jarvis,project"
)

results = search(
    "what is my name"
)

for m in results:

    print(m)