"""
JARVIS PRO
Developer Editor

Response Parser Test
"""

print("TEST_PARSER LOADED")

from brain.developer.editor.parser import ResponseParser


def main():

    response = """# FILE: src/main.py
```python
def add(a, b):
    return a + b

print("Hello World")
```

"""

    print("=" * 80)
    print("INPUT RESPONSE")
    print("=" * 80)
    print(response)
    print("=" * 80)

    parser = ResponseParser()

    result = parser.parse(response)

    print()
    print("=" * 80)
    print("PARSER RESULT")
    print("=" * 80)

    print("Success      :", result.success)
    print("Message      :", result.message)
    print("Patch Count  :", len(result.patches))
    
    print()

    for i, patch in enumerate(result.patches, start=1):

        print("-" * 80)
        print(f"PATCH #{i}")
        print("-" * 80)

        print("Path     :", patch.path)
        print("Language :", patch.language)

        print("\nContent")
        print("-" * 80)
        print(patch.content)
        print()

    print("=" * 80)

if __name__ == "__main__":
    main()