from brain.developer.developer_parser import DeveloperParser

parser = DeveloperParser()

text = """
# main.py

print("Hello")

# utils.py

def add(a, b):
    return a + b

# folder/test.py

print("Nested")
"""

result = parser.parse(text)

print("=" * 60)
print("SUCCESS")
print("=" * 60)

print(result.success)

print()

for name, code in result.files.items():

    print(name)

    print("-" * 40)

    print(code)

    print()
    
    
tests = """

File: app.py

print("A")

Filename: utils.py

def add():
    pass

## index.html

<html></html>

<!-- style.css -->

body{}

"""

parser = DeveloperParser()

result = parser.parse(tests)

for name, code in result.files.items():

    print("=" * 50)

    print(name)

    print("-" * 50)

    print(code)

    print()