# from ai.memory_store import remember

# remember(
#     key="college",
#     value="VVCE Mysore",
#     category="education",
#     keywords="college,education",
#     importance=4
# )

# remember(
#     key="project",
#     value="JARVIS PRO",
#     category="project",
#     keywords="project",
#     importance=4
# )

# remember(
#     key="favorite_language",
#     value="Python",
#     category="preference",
#     keywords="language,favorite",
#     importance=3
# )

# remember(
#     key="email",
#     value="madan23062004@example.com",
#     category="contact",
#     keywords="email",
#     importance=5
# )


from ai.memory import init_memory
from ai.memory_answer import answer

init_memory()

tests = [

    "What is my name?",
    "Who am I?",
    "Tell me my name",

    "Where do I study?",
    "Which college do I study at?",
    "Which university?",

    "What is my project?",
    "Which project am I am working on?",

    "What is my email?",
    "What is my phone number?",

    "What is my favorite language?"
]

for q in tests:

    print("-" * 50)
    print("USER   :", q)
    print("JARVIS :", answer(q))