import re

from voice.manager import speak
from archive.plugins import register as plugin_register
from core.registry import register as ai_register

from ai.memory_store import (
    remember,
    forget,
    get as recall,
    list_all as list_memory
)

from ai.memory_store import (
    remember,
    forget,
    get,
    list_all
)


def memory_command(query):

    print("QUERY:", query)

    query = query.lower()

    # ---------------- REMEMBER ----------------

    m = re.search(r"remember my (.+?) is (.+)", query)

    print("Remember Match =", m)

    if m:

        key = m.group(1).strip()
        value = m.group(2).strip()

        print("KEY =", key)
        print("VALUE =", value)

        remember(key, value)

        print("Saved successfully!")

        speak(f"I'll remember your {key}")

        return True

    # ---------------- RECALL ----------------

    m = re.search(r"what(?:'s| is) my (.+)", query)

    print("Recall Match =", m)

    if m:

        key = m.group(1).strip()

        print("Looking for:", key)

        value = recall(key)

        print("Database returned:", value)

        if value:
            print(f"Your {key} is {value}")
        else:
            speak(f"I don't know your {key} yet.")

        return True

    print("No pattern matched")

    return False

def ai_remember(data):

    key = data["key"]
    value = data["value"]

    remember(key,value)

    speak(f"I'll remember your {key}")

    return True


def ai_recall(data):

    key = data["key"]

    value = recall(key)

    if value:
        speak(value)
    else:
        speak("I don't know.")

    return True


plugin_register(
    [
        "remember",
        "what is my",
        "what's my"
    ],
    memory_command
)

def recall(key):

    memory = get(key)

    if memory:

        return memory.value

    return None


def list_memory():

    return [

        (m.key, m.value)

        for m in list_all()

    ]

ai_register("remember", ai_remember)
ai_register("recall", ai_recall)