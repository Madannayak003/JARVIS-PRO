from brain.developer.developer_parser import DeveloperParser

text = """
Here is your project.

```html
<!-- index.html -->
<html>
<h1>Hello</h1>
</html>
```

```css
/* style.css */

body{
background:black;
}
```

```javascript
// script.js

console.log("Hello");
```

"""

parser = DeveloperParser()

result = parser.parse(text)

print()

print(result)

print()

for filename, content in result.files.items():
    print("=" * 60)

    print(filename)

    print("-" * 60)

    print(content)

    print()