from brain.developer.engine.syntax_validator import SyntaxValidator

validator = SyntaxValidator()

tests = [

    (
        "calculator.py",
        "print('Hello')",
    ),

    (
        "broken.py",
        "print(",
    ),

    (
        "index.html",
        "<html><body>Hello</body></html>",
    ),

    (
        "broken.html",
        "<html><body>",
    ),

    (
        "style.css",
        "body { color:red; }",
    ),

    (
        "bad.css",
        "body { color:red;",
    ),

]

for filename, code in tests:

    result = validator.validate(
        filename,
        code
    )

    print("=" * 60)
    print(filename)
    print("Success :", result.success)
    print("Language:", result.language)

    if not result.success:
        print("Error   :", result.error)