"""Focused tests for display-preserving Markdown-to-speech normalization."""

from __future__ import annotations

import unittest

from voice.speech_text import (
    clean_for_speech,
    clean_for_speech_stateful,
)


MARKDOWN_RESPONSE = """## Python Decorator Example

Here is a simple example.

1. Core concept
- A decorator wraps a function.

---

```python
def deco(func):
    return func
```

Use `@deco` and see [the docs](https://example.com)."""


class SpeechTextTests(unittest.TestCase):
    def test_sanitizer_removes_presentation_and_code_for_voice(self):
        spoken = clean_for_speech(MARKDOWN_RESPONSE)

        self.assertIn("Python Decorator Example", spoken)
        self.assertIn("A decorator wraps a function", spoken)
        self.assertIn("the docs", spoken)
        self.assertNotIn("```", spoken)
        self.assertNotIn("##", spoken)
        self.assertNotIn("---", spoken)
        self.assertNotIn("def deco", spoken)
        self.assertNotIn("1.", spoken)

    def test_fenced_code_state_survives_streamed_chunks(self):
        first, in_code = clean_for_speech_stateful(
            "Here is code. ```python",
        )
        second, in_code = clean_for_speech_stateful(
            "def deco(func):\n    return func\n``` Done.",
            in_code,
        )

        self.assertEqual(first, "Here is code.")
        self.assertEqual(second, "Done.")
        self.assertFalse(in_code)

    def test_original_display_text_is_not_mutated(self):
        original = MARKDOWN_RESPONSE
        clean_for_speech(original)

        self.assertIn("## Python Decorator Example", original)
        self.assertIn("```python", original)
        self.assertIn("def deco", original)


if __name__ == "__main__":
    unittest.main()
