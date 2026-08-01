import requests

from ai.stream import generate_stream

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


# -----------------------------
# Planner / Normal Chat
# Returns FULL STRING
# -----------------------------
def ask_ollama(system, prompt):
    
# -------------------------------------
# MODELES = jarvis,qwen2.5:3b,qwen3:4b      
# --------------------------------------    
    
    MODEL = "jarvis"
    
    print("AI : Sending POST request...")
    
    print("DEBUG 1 : Before requests.post()")
    
    print(f"System Prompt Length : {len(system)}")
    print(f"User Prompt Length   : {len(prompt)}")
    print(f"Total Characters     : {len(system) + len(prompt)}")
    
    print("\n========== USER PROMPT ==========\n")
    print(prompt[:3000])      # First 3000 characters
    print("\n=================================\n")
    
    #-----------------------------
    # POST request to Ollama API
    #-----------------------------

    try:

        response = requests.post(

            OLLAMA_URL,

            json={
                "model": MODEL,
                "system": system,
                "prompt": prompt,
                "stream": False,
            },

            timeout=(10, 300)

        )

    except requests.exceptions.ReadTimeout:

        print("\n" + "=" * 80)
        print("ERROR : Ollama generation timed out.")
        print("=" * 80)

        return ""

    except requests.exceptions.RequestException as e:

        print("\n" + "=" * 80)
        print("ERROR :", e)
        print("=" * 80)

        return ""
    
    print("DEBUG 2 : requests.post() finished")
    
    print("AI : POST request finished")

    response.raise_for_status()
    
    print("HTTP Status :", response.status_code)
    
    print("AI : Returning response")

    # return response.json()["response"]
    
    data = response.json()
    
    print("DEBUG 3 : JSON parsed")

    print("JSON Keys :", data.keys())

    print("Done Flag :", data.get("done"))

    print("Response Length :", len(data.get("response", "")))

    return data["response"]


# -----------------------------
# AI Engine V2
# Returns STREAM
# -----------------------------
def ask_ollama_stream(system, prompt, stop_event=None):

    return generate_stream(
        system,
        prompt,
        stop_event
    )