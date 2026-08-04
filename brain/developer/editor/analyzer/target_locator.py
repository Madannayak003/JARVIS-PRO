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
    files that are relevant to the user's request.
    """

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

        # -------------------------------------
        # Extract words from request
        # -------------------------------------

        words = {

            word.lower()

            for word in re.findall(

                r"[A-Za-z_][A-Za-z0-9_]*",

                request,

            )

        }

        # -------------------------------------
        # Exact filename match
        # Example:
        # "format main.py"
        # -------------------------------------

        for file in index.files:

            filename = file.split("/")[-1].lower()

            if filename in request:

                selected.add(file)

        # -------------------------------------
        # Partial filename match
        # Example:
        # parser -> parser.py
        # login -> login.py
        # -------------------------------------

        for file in index.files:

            filename = file.split("/")[-1].lower()

            stem = filename.rsplit(".", 1)[0]

            if stem in words:

                selected.add(file)

        # -------------------------------------
        # Function names
        # -------------------------------------

        for word in words:

            if word in index.functions:

                selected.update(

                    index.functions[word]

                )

        # -------------------------------------
        # Class names
        # -------------------------------------

        for word in words:

            if word in index.classes:

                selected.update(

                    index.classes[word]

                )

        # -------------------------------------
        # Imported modules
        # -------------------------------------

        for word in words:

            if word in index.imports:

                selected.update(

                    index.imports[word]

                )

        # -------------------------------------
        # Fallback
        #
        # If nothing matched,
        # temporarily return every file.
        #
        # This will later be replaced by
        # smarter ranking.
        # -------------------------------------

        if not selected:

            return sorted(index.files)

        return sorted(selected)