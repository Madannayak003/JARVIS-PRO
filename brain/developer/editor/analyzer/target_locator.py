"""
JARVIS PRO
Developer Editor

Target Locator
"""

from pathlib import Path


class TargetLocator:
    """
    Finds candidate files that should be edited.
    """

    DEFAULT_EXTENSIONS = {

        ".py",
        ".ino",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".html",
        ".css",
        ".js",
        ".ts",
        ".json",
        ".md",

    }

    # --------------------------------------------------

    def locate(
        self,
        project_path: str,
    ) -> list[str]:
        """
        Locate editable files.
        """

        root = Path(project_path)

        if not root.exists():

            return []

        files = []

        for path in root.rglob("*"):

            if not path.is_file():

                continue

            if path.suffix.lower() not in self.DEFAULT_EXTENSIONS:

                continue

            files.append(

                str(

                    path.relative_to(root)

                ).replace("\\", "/")

            )

        return sorted(files)