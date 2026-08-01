from ai.memory import init_memory
from ai.memory_manager import learn
from ai.memory_store import get

init_memory()

tests = [

    "My name is Madan R",

    "My name is Madan R",          # duplicate

    "My college is NIE Mysore",

    "My college is MIT",           # update

    "My favorite language is Python",

    "Today is hot"                 # should not save

]

for t in tests:

    print("\nUSER:", t)

    print(learn(t))

print("\nName Memory:")

print(get("name"))

print("\nCollege Memory:")

print(get("college"))

print("\nLanguage Memory:")

print(get("favorite_language"))