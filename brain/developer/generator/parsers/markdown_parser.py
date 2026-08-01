"""
JARVIS PRO
Developer Generator

Markdown Parser
"""

import re

from brain.developer.generator.models.generated_file import GeneratedFile
from brain.developer.generator.models.generated_project import GeneratedProject


class MarkdownParser:
    """
    Parses Markdown returned by an LLM into a GeneratedProject.
    """

    # ---------------------------------------------------------
    # Supported format
    #
    # # FILE: src/main.py
    # ```python
    # ...
    # ```
    # ---------------------------------------------------------

    FILE_PATTERN = re.compile(

        r"^\s*#\s*FILE:\s*(.+?)\s*\n```([\w+-]*)\n(.*?)```",

        re.MULTILINE | re.DOTALL | re.IGNORECASE,

    )
    
    # ---------------------------------------------------------

    def parse(
        self,
        response: str,
    ) -> GeneratedProject:
        """
        Parse Markdown into a GeneratedProject.
        """

        project = GeneratedProject()

        matches = self.FILE_PATTERN.findall(response)

        if not matches:

            project.generated = False

            project.errors.append(

                "No project files found in AI response."

            )

            return project

        # --------------------------------------------

        for path, markdown_language, content in matches:

            path = path.strip().replace("\\", "/")
            
            if not path:
                continue

            content = content.rstrip("\n\r")

            generated_file = GeneratedFile(

                name=self._get_name(path),

                path=path,

                extension=self._get_extension(path),

                content=content,

                language=self._get_language(path),

                markdown_language=markdown_language,

                size=len(content.encode("utf-8")),

                line_count=len(content.splitlines()),

                is_empty=len(content.strip()) == 0,

            )

            project.files.append(generated_file)

        # --------------------------------------------

        project.generated = len(project.files) > 0

        project.file_count = len(project.files)

        project.total_characters = sum(

            file.size

            for file in project.files

        )

        return project

    # ---------------------------------------------------------

    @staticmethod
    def _get_name(path: str) -> str:

        return path.replace("\\", "/").split("/")[-1]

    # ---------------------------------------------------------

    @staticmethod
    def _get_extension(path: str) -> str:

        if "." not in path:

            return ""

        return "." + path.split(".")[-1].lower()

    # ---------------------------------------------------------

    @staticmethod
    def _get_language(path: str) -> str:

        extension = MarkdownParser._get_extension(path)

        languages = {

            ".py": "Python",

            ".cpp": "C++",

            ".c": "C",

            ".h": "C++",

            ".hpp": "C++",

            ".ino": "Arduino",
            
            ".java": "Java",
            
            ".kt": "Kotlin",
            
            ".cs": "C#",
            
            ".go": "Go",
            
            ".rs": "Rust",
            
            ".php": "PHP",
            
            ".sh": "Shell",
            
            ".bat": "Batch",
            
            ".ps1": "PowerShell",
            
            ".sql": "SQL",
            
            ".dart": "Dart",
            
            ".swift": "Swift",
            
            ".vue": "Vue",
            
            ".jsx": "React",
            
            ".tsx": "React",

            ".html": "HTML",

            ".css": "CSS",

            ".js": "JavaScript",

            ".ts": "TypeScript",

            ".json": "JSON",

            ".md": "Markdown",

            ".txt": "Text",

            ".xml": "XML",

            ".yml": "YAML",

            ".yaml": "YAML",

            ".ini": "INI",

        }

        return languages.get(extension, "")