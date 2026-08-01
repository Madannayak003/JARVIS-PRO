from voice.manager import speak
from core.registry import register
from core.action_memory import set_memory

from core.confirmation import ask


def ai_clarify(data):

    question = data.get(
        "question",
        "Can you please clarify?"
    )
    
    context = data.get("context")

    if context:

        set_memory(
            "clarify_context", 
            context)

    # Save clarification request
    ask(
        "clarify",
        data
    )

    speak(question)

    return True


register("clarify", ai_clarify)