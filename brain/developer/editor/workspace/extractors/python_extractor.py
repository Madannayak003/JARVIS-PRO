"""
JARVIS PRO
Developer Editor

Python Extractor
"""

import ast

from brain.developer.editor.workspace.extractors.base_extractor import (
    BaseExtractor,
)


class PythonExtractor(BaseExtractor):
    """
    AST-based extractor for Python files.
    """

    FULL_FILE_ACTIONS = {

        "FORMAT",

    }

    # --------------------------------------------------

    def extract(
        self,
        request: str,
        edit_type: str,
        content: str,
    ) -> str:

        if not content:

            return ""

        if edit_type in self.FULL_FILE_ACTIONS:

            return content

        try:

            tree = ast.parse(content)

        except Exception:

            return content

        request = request.lower()

        lines = content.splitlines()

        for node in ast.walk(tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                if node.name.lower() not in request:

                    continue

                start = node.lineno - 1

                end = getattr(

                    node,

                    "end_lineno",

                    start + 1,

                )

                return "\n".join(

                    lines[start:end]

                )

            if isinstance(node, ast.ClassDef):

                if node.name.lower() not in request:

                    continue

                start = node.lineno - 1

                end = getattr(

                    node,

                    "end_lineno",

                    start + 1,

                )

                return "\n".join(

                    lines[start:end]

                )

        return "\n".join(lines[:100])