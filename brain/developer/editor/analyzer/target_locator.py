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

        # ------------------------------------------
        # Remove common edit verbs
        # ------------------------------------------

        IGNORE_WORDS = {

            "fix",
            "add",
            "remove",
            "replace",
            "rename",
            "update",
            "format",
            "optimize",
            "refactor",
            "implement",
            "insert",
            "delete",
            "repair",
            "solve",

        }

        words -= IGNORE_WORDS

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
        # Partial filename match
        # +60
        # Example:
        # divide -> math/divide.py
        # --------------------------------------------------

        for file in index.files:

            filename = file.split("/")[-1].lower()

            stem = filename.rsplit(".", 1)[0]

            for word in words:

                if word in stem:

                    scores[file] += 60

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

            for function_name, files in index.functions.items():

                if word == function_name.lower():

                    for file in files:

                        scores[file] += 90

                elif word in function_name.lower():

                    for file in files:

                        scores[file] += 70

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
        # Prefer source files
        # --------------------------------------------------

        for file in scores:

            if file.endswith(

                (

                    ".py",

                    ".cpp",

                    ".ino",

                    ".c",

                    ".h",

                    ".hpp",

                )

            ):

                scores[file] += 5

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