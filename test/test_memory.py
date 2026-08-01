from ai.memory import init_memory
from ai.memory_store import remember, get, list_all

init_memory()

remember(
    "name",
    "Madan R"
)

m = get("name")

print(m)

print(m.value)

print(list_all())