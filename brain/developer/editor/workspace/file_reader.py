"""
JARVIS PRO
Developer Editor

File Reader
"""

from pathlib import Path


class FileReader:
    """
    Reads the contents of selected files.
    """

    # --------------------------------------------------

    def read(
        self,
        project_path: str,
        files: list[str],
    ) -> dict[str, str]:
        """
        Read selected project files.

        Returns:
            {
                "src/main.py": "...",
                "README.md": "...",
            }
        """

        result: dict[str, str] = {}

        root = Path(project_path)

        for relative_path in files:

            file_path = root / relative_path

            try:

                result[relative_path] = file_path.read_text(

                    encoding="utf-8",

                )

            except Exception:

                result[relative_path] = ""

        return result