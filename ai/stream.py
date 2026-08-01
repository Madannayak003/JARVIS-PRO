"""
JARVIS PRO
Ollama Streaming Engine

Streams responses from Ollama while supporting interruption.

Author: Madan
"""

import json
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# --------------------------------------
# Available Models:
# jarvis
# qwen2.5:3b
# qwen3:4b
# --------------------------------------
MODEL = "jarvis"


def generate_stream(system, prompt, stop_event=None):
    """
    Stream response from Ollama.

    Yields:
        dict:
        {
            "response": "...",
            "done": False
        }
    """

    response = None

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "system": system,
                "prompt": prompt,
                "stream": True,

                # "think": False
            },
            stream=True,
            timeout=(10, None)
        )

        response.raise_for_status()

        for line in response.iter_lines():

            # Stop streaming if requested
            if stop_event is not None and stop_event.is_set():

                print("\n[STREAM] Interrupted")

                break

            if not line:
                continue

            try:

                chunk = json.loads(line.decode("utf-8"))

            except json.JSONDecodeError:

                continue

            # Keep original behaviour
            yield chunk

            # Finished generating
            if chunk.get("done", False):
                break

    except requests.exceptions.RequestException as e:

        print(f"[OLLAMA ERROR] {e}")

    finally:

        if response is not None:
            response.close()