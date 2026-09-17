"""Regression tests for single-file and multi-file web project editing."""

from brain.developer.editor.editor import Editor


def _file_response(path: str, language: str, content: str) -> str:
    return f"# FILE: {path}\n```{language}\n{content}\n```"


def _single_file_html(padding: str = "") -> str:
    return """<!doctype html>
<html>
<head>
<style>
:root { --background: white; }
.hero { color: navy; }
</style>
</head>
<body>
<!-- preserve this comment -->
<button id="existing-action">Existing action</button>
<script>
const existingFeature = () => "keep me";
</script>
""" + padding + "\n<!-- end-of-original-file -->\n</body>\n</html>\n"


def _edit_embedded_css(content: str) -> str:
    return content.replace(
        ".hero { color: navy; }",
        ".hero { color: navy; }\n.theme-toggle { color: white; background: navy; }",
    )


def test_single_file_html_edit_receives_and_preserves_complete_file(tmp_path):
    original = _single_file_html()
    (tmp_path / "index.html").write_text(original, encoding="utf-8")
    editor = Editor()

    def generate(prompt):
        assert "index.html" in prompt.user_prompt
        assert "<!-- end-of-original-file -->" in prompt.user_prompt
        return _file_response("index.html", "html", _edit_embedded_css(original))

    editor.provider.generate = generate
    result = editor.execute(
        "update page CSS to add a theme toggle button",
        str(tmp_path),
    )

    written = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert result.success
    assert ".theme-toggle" in written
    assert "<!-- preserve this comment -->" in written
    assert 'const existingFeature = () => "keep me";' in written
    assert "<!-- end-of-original-file -->" in written


def test_multi_file_css_edit_changes_only_the_existing_stylesheet(tmp_path):
    index = "<link rel=\"stylesheet\" href=\"style.css\">\n<div>Home</div>\n"
    style = ".hero { color: navy; }\n"
    script = "const existingFeature = () => 'keep me';\n"
    (tmp_path / "index.html").write_text(index, encoding="utf-8")
    (tmp_path / "style.css").write_text(style, encoding="utf-8")
    (tmp_path / "script.js").write_text(script, encoding="utf-8")
    editor = Editor()

    editor.provider.generate = lambda prompt: _file_response(
        "style.css",
        "css",
        ".hero { color: navy; }\n.theme-toggle { color: white; background: navy; }",
    )

    result = editor.execute(
        "update CSS to add a theme toggle button",
        str(tmp_path),
    )

    assert result.success
    assert ".theme-toggle" in (tmp_path / "style.css").read_text(encoding="utf-8")
    assert (tmp_path / "index.html").read_text(encoding="utf-8") == index
    assert (tmp_path / "script.js").read_text(encoding="utf-8") == script


def test_incomplete_large_single_file_response_is_rejected(tmp_path):
    original = _single_file_html("<!-- padding -->" * 5_500)
    assert len(original) > 80_000
    (tmp_path / "index.html").write_text(original, encoding="utf-8")
    editor = Editor()

    editor.provider.generate = lambda prompt: _file_response(
        "index.html", "html", original[:14_000]
    )
    result = editor.execute("update CSS theme", str(tmp_path))

    assert not result.success
    assert (tmp_path / "index.html").read_text(encoding="utf-8") == original


def test_complete_large_single_file_response_is_accepted(tmp_path):
    original = _single_file_html("<!-- padding -->" * 5_500)
    assert len(original) > 80_000
    (tmp_path / "index.html").write_text(original, encoding="utf-8")
    editor = Editor()
    modified = _edit_embedded_css(original)

    def generate(prompt):
        assert len(prompt.user_prompt) > 80_000
        assert "<!-- end-of-original-file -->" in prompt.user_prompt
        return _file_response("index.html", "html", modified)

    editor.provider.generate = generate
    result = editor.execute("update CSS theme", str(tmp_path))

    written = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert result.success
    assert ".theme-toggle" in written
    assert "<!-- end-of-original-file -->" in written
    assert len(written) >= len(original)
