"""
JARVIS PRO
Developer Editor

Target Locator
"""

import re

from collections import defaultdict

from brain.developer.editor.models.project_index import (
    ProjectIndex,
)


class TargetLocator:
    """
    Uses a scoring system to locate the
    most relevant project files.
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

    MAX_RESULTS = 5

    # --------------------------------------------------

    def locate(
        self,
        request: str,
        index: ProjectIndex,
    ) -> list[str]:

        if index is None:

            return []

        request = request.lower()

        words = {

            word.lower()

            for word in re.findall(

                r"[A-Za-z_][A-Za-z0-9_]*",

                request,

            )

        }

        scores = defaultdict(int)

        # --------------------------------------------------
        # Exact filename
        # +100
        # --------------------------------------------------

        for file in index.files:

            filename = file.split("/")[-1].lower()

            if filename in request:

                scores[file] += 100

        # --------------------------------------------------
        # Filename stem
        # +80
        # --------------------------------------------------

        for file in index.files:

            filename = file.split("/")[-1].lower()

            stem = filename.rsplit(".", 1)[0]

            if stem in words:

                scores[file] += 80

        # --------------------------------------------------
        # Common project files
        # +50
        # --------------------------------------------------

        for keyword, value in self.COMMON_FILES.items():

            if keyword not in words:

                continue

            for file in index.files:

                if value in file.lower():

                    scores[file] += 50

        # --------------------------------------------------
        # Functions
        # +90
        # --------------------------------------------------

        for word in words:

            if word not in index.functions:

                continue

            for file in index.functions[word]:

                scores[file] += 90

        # --------------------------------------------------
        # Classes
        # +85
        # --------------------------------------------------

        for word in words:

            if word not in index.classes:

                continue

            for file in index.classes[word]:

                scores[file] += 85

        # --------------------------------------------------
        # Imports
        # +40
        # --------------------------------------------------

        for word in words:

            if word not in index.imports:

                continue

            for file in index.imports[word]:

                scores[file] += 40

        # --------------------------------------------------
        # Nothing matched
        # --------------------------------------------------

        if not scores:

            return []

        # --------------------------------------------------
        # Highest score first
        # --------------------------------------------------

        ranked = sorted(

            scores.items(),

            key=lambda item: (

                -item[1],

                item[0],

            ),

        )

        return [

            file

            for file, _ in ranked[: self.MAX_RESULTS]

        ]