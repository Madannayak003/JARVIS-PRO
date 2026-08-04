"""
JARVIS PRO
Developer Editor

Instruction Builder
"""


class InstructionBuilder:
    """
    Builds editing instructions for the LLM.
    """

    def build(self) -> str:

        return "\n".join(

            [

                "# Instructions",

                "",

                "Modify ONLY the selected files.",

                "Preserve the existing coding style.",

                "Do not rewrite unrelated code.",

                "Do not modify files that are not listed.",

                "Do not rename files unless explicitly requested.",

                "Do not create new files unless explicitly requested.",

                "Do not delete code unless explicitly requested.",

                "Keep existing formatting unless the request is to format the file.",

                "",

                "# Output Format",

                "",

                "Return ONLY modified files.",

                "Return NOTHING except valid '# FILE:' blocks.",

                "Do not include explanations.",

                "Do not include markdown outside file blocks.",

                "Do not include comments outside the files.",

                "Do not return unchanged files.",

                "",

                "Required format:",

                "",

                "# FILE: <relative_path>",

                "```<language>",

                "<complete modified file contents>",

                "```",

                "",

                "Example:",

                "",

                "# FILE: src/main.py",

                "```python",

                "print('Hello World')",

                "```",

            ]

        )