"""
JARVIS PRO
Developer Editor

Target Locator
"""

import re

from brain.developer.editor.models.project_index import (
    ProjectIndex,
)


class TargetLocator:
    """
    Uses the ProjectIndex to intelligently locate
    files relevant to the user's request.
    """

    COMMON_FILES = {

        "readme": "readme",

        "license": "license",

        "requirements": "requirements",

        "main": "main",

        "test": "test",

        "config": "config",

        "settings": "settings",

    }

    # --------------------------------------------------

    def locate(
        self,
        request: str,
        index: ProjectIndex,
    ) -> list[str]:

        if index is None:

            return []

        request = request.lower()

        selected = set()

        words = {

            word.lower()

            for word in re.findall(

                r"[A-Za-z_][A-Za-z0-9_]*",

                request,

            )

        }

        # --------------------------------------------------
        # Exact filename
        # --------------------------------------------------

        for file in index.files:

            filename = file.split("/")[-1].lower()

            if filename in request:

                selected.add(file)

        # --------------------------------------------------
        # Filename without extension
        # --------------------------------------------------

        for file in index.files:

            filename = file.split("/")[-1].lower()

            stem = filename.rsplit(".", 1)[0]

            if stem in words:

                selected.add(file)

        # --------------------------------------------------
        # Common project files
        # --------------------------------------------------

        for keyword, value in self.COMMON_FILES.items():

            if keyword not in words:

                continue

            for file in index.files:

                if value in file.lower():

                    selected.add(file)

        # --------------------------------------------------
        # Function names
        # --------------------------------------------------

        for word in words:

            if word in index.functions:

                selected.update(

                    index.functions[word]

                )

        # --------------------------------------------------
        # Class names
        # --------------------------------------------------

        for word in words:

            if word in index.classes:

                selected.update(

                    index.classes[word]

                )

        # --------------------------------------------------
        # Imports
        # --------------------------------------------------

        for word in words:

            if word in index.imports:

                selected.update(

                    index.imports[word]

                )

        # --------------------------------------------------
        # Smart fallback
        # --------------------------------------------------

        if selected:

            return sorted(selected)

        # Prefer source files over documentation

        source = [

            file

            for file in index.files

            if file.endswith(

                (

                    ".py",

                    ".ino",

                    ".cpp",

                    ".c",

                    ".h",

                    ".hpp",

                    ".js",

                    ".ts",

                    ".html",

                    ".css",

                )

            )

        ]

        if source:

            return sorted(source)

        return sorted(index.files)