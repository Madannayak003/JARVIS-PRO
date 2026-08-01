import json

from ai.ollama import ask_ollama

def fallback(step):

    prompt = f"""
This action is unsupported.

{json.dumps(step)}

Convert it into supported actions.

Supported:

open
youtube_search
google_search
play
volume
remember
recall
clarify

Return ONLY JSON.
"""

    answer = ask_ollama("", prompt)

    return answer