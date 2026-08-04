"""
JARVIS PRO
Developer Editor

Prompt Builder
"""

from brain.developer.editor.models.edit_request import (
    EditRequest,
)

from brain.developer.editor.models.prompt_context import (
    PromptContext,
)

from brain.developer.editor.models.prompt_result import (
    PromptResult,
)

from brain.developer.editor.prompt_builder.system_builder import (
    SystemBuilder,
)

from brain.developer.editor.prompt_builder.context_builder import (
    ContextBuilder,
)

from brain.developer.editor.prompt_builder.instruction_builder import (
    InstructionBuilder,
)


class PromptBuilder:

    def __init__(self):

        self.system_builder = SystemBuilder()

        self.context_builder = ContextBuilder()

        self.instruction_builder = InstructionBuilder()

    # --------------------------------------------------

    def build(
        self,
        request: EditRequest,
    ) -> PromptResult:

        context = PromptContext(

            request=request,

        )

        system = self.system_builder.build(

            context,

        )

        user = (

            self.context_builder.build(

                context,

            )

            + "\n\n"

            + self.instruction_builder.build()

        )

        return PromptResult(

            system_prompt=system,

            user_prompt=user,

            prompt=system + "\n\n" + user,

        )