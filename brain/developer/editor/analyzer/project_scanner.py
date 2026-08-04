"""
JARVIS PRO
Developer Editor

Project Scanner
"""

import ast
from pathlib import Path

from brain.developer.editor.models.project_index import (
    ProjectIndex,
)


class ProjectScanner:
    """
    Scans a project and builds a ProjectIndex.
    """

    SUPPORTED_EXTENSIONS = {

        ".py",

        ".ino",

        ".cpp",

        ".c",

        ".h",

        ".hpp",

    }

    # --------------------------------------------------

    def scan(
        self,
        project_path: str,
    ) -> ProjectIndex:

        index = ProjectIndex()

        root = Path(project_path)

        if not root.exists():

            return index

        for file in root.rglob("*"):

            if not file.is_file():

                continue

            if file.suffix.lower() not in self.SUPPORTED_EXTENSIONS:

                continue

            relative = str(

                file.relative_to(root)

            ).replace("\\", "/")

            index.files.append(

                relative,

            )

            if file.suffix.lower() == ".py":

                self._scan_python(

                    file,

                    relative,

                    index,

                )

        return index

    # --------------------------------------------------

    def _scan_python(

        self,

        file: Path,

        relative: str,

        index: ProjectIndex,

    ):

        try:

            tree = ast.parse(

                file.read_text(

                    encoding="utf-8",

                )

            )

        except Exception:

            return

        for node in ast.walk(tree):

            # ----------------------

            if isinstance(

                node,

                ast.FunctionDef,

            ):

                index.functions.setdefault(

                    node.name,

                    [],

                ).append(

                    relative,

                )

            # ----------------------

            elif isinstance(

                node,

                ast.ClassDef,

            ):

                index.classes.setdefault(

                    node.name,

                    [],

                ).append(

                    relative,

                )

            # ----------------------

            elif isinstance(

                node,

                ast.Import,

            ):

                for alias in node.names:

                    index.imports.setdefault(

                        alias.name,

                        [],

                    ).append(

                        relative,

                    )

            # ----------------------

            elif isinstance(

                node,

                ast.ImportFrom,

            ):

                module = node.module or ""

                index.imports.setdefault(

                    module,

                    [],

                ).append(

                    relative,

                )