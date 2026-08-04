"""
JARVIS PRO
Developer Editor

Instruction Builder
"""


class InstructionBuilder:

    def build(self) -> str:

        return "\n".join(

            [

                "# Instructions",

                "",

                "Modify only the selected files.",

                "Preserve formatting.",

                "Do not rename files.",

                "Do not create additional files unless requested.",

                "Do not remove unrelated code.",

                "Return only modified '# FILE:' blocks.",

            ]

        )