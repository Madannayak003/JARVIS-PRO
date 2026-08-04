"""
JARVIS PRO
Developer Editor

Code Extractor
"""

import re


class CodeExtractor:
    """
    Extracts only the relevant code that should
    be sent to the LLM.
    """

    CONTEXT_LINES = 20

    # --------------------------------------------------

    def extract(
        self,
        request: str,
        file_contents: dict[str, str],
    ) -> dict[str, str]:

        result = {}

        request = request.lower()

        # -------------------------------------
        # Look for function/class names
        # -------------------------------------

        words = re.findall(

            r"[A-Za-z_][A-Za-z0-9_]*",

            request,

        )

        for path, content in file_contents.items():

            snippet = self._extract_snippet(

                content,

                words,

            )

            result[path] = snippet

        return result

    # --------------------------------------------------

    def _extract_snippet(

        self,

        content: str,

        words: list[str],

    ) -> str:

        if not content:

            return ""

        lines = content.splitlines()

        for index, line in enumerate(lines):

            lower = line.lower()

            for word in words:

                if word in lower:

                    start = max(

                        0,

                        index - self.CONTEXT_LINES,

                    )

                    end = min(

                        len(lines),

                        index + self.CONTEXT_LINES,

                    )

                    return "\n".join(

                        lines[start:end]

                    )

        return content