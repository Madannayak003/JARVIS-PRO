from ai.query_parser import extract_keywords

tests = [

    "What is my name?",

    "Who am I?",

    "Tell me about my project.",

    "What is my college name?",

    "Where is my home?",

]

for t in tests:

    print(t)

    print(extract_keywords(t))

    print()