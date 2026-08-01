"""
JARVIS PRO
Memory Answer Engine

Responsibilities
----------------
✓ Instant personal memory answers
✓ Direct memory lookup
✓ Semantic fallback
✓ No Ollama required
"""

import re
from ai.memory_store import get
from ai.memory_search import search
from ai.memory_profile import profile_summary

# ---------------------------------------
# Question Aliases
# ---------------------------------------

QUESTION_ALIASES = {

    "name": [
        "name",
        "who am i",
        "full name",
        "myself",
        "identity"
    ],

    "college": [
        "college",
        "study",
        "university",
        "institution",
        "campus"
    ],

    "project": [
        "project",
        "working on",
        "final year project"
    ],

    "birthday": [
        "birthday",
        "birth date",
        "date of birth",
        "dob"
    ],

    "phone": [
        "phone",
        "mobile",
        "number",
        "phone number"
    ],

    "email": [
        "email",
        "mail",
        "gmail",
        "email address"
    ],

    "favorite_language": [
        "favorite language",
        "favourite language",
        "programming language",
        "language"
    ],
    
    "os": [

    "operating system",

    "windows",

    "os"

    ],

    "laptop_brand": [

        "laptop",

        "computer",

        "pc"

    ],

    "preferred_browser": [

        "browser",

        "chrome",

        "firefox"

    ],

    "preferred_editor": [

        "editor",

        "vs code",

        "vscode"

    ],

    "preferred_theme": [

        "theme",

        "dark mode",

        "light mode"

    ]
}


# ---------------------------------------
# Response Templates
# ---------------------------------------

RESPONSES = {

    "name":
        "Your name is {value}.",

    "college":
        "You study at {value}.",

    "project":
        "Your project is {value}.",

    "birthday":
        "Your date of birth is {value}.",

    "phone":
        "Your phone number is {value}.",

    "email":
        "Your email address is {value}.",

    "favorite_language":
        "Your favorite programming language is {value}.",
    
    "os":
    "You use {value}.",

    "laptop_brand":
        "Your laptop is {value}.",

    "preferred_browser":
        "Your preferred browser is {value}.",

    "preferred_editor":
        "Your preferred editor is {value}.",

    "preferred_theme":
        "You prefer {value}.",

    "favorite_drink":
        "Your favorite drink is {value}."
}


# ---------------------------------------
# Personal Question Detector
# ---------------------------------------

PERSONAL_PATTERNS = [

    r"\bmy\b",
    r"\bme\b",
    r"\bmine\b",

    r"\bwho am i\b",

    r"\bwhat is my\b",
    r"\bwhere do i\b",
    r"\bwhich\b.*\bdo i\b",
    r"\bdo i\b",
    r"\bdid i\b",

    r"\bi study\b",
    r"\bi work\b",
    r"\bi live\b"

]


def is_personal_question(question):

    question = question.lower().strip()

    for pattern in PERSONAL_PATTERNS:

        if re.search(pattern, question):

            return True

    return False
    

# ---------------------------------------
# Normalize Question
# ---------------------------------------

def normalize_question(question):

    question = question.lower().strip()

    for key, aliases in QUESTION_ALIASES.items():

        for alias in aliases:

            if alias in question:

                return key

    return None


# ---------------------------------------
# Direct Lookup
# ---------------------------------------

def direct_answer(question):

    key = normalize_question(question)

    if not key:

        return None

    memory = get(key)

    # -----------------------
    # Direct Match
    # -----------------------

    if memory:

        template = RESPONSES.get(key)

        if template:

            return template.format(

                value=memory.value

            )

        return memory.value

    # -----------------------
    # Semantic Search
    # -----------------------

    memories = search(question, limit=1)

    if memories:

        memory = memories[0]

        template = RESPONSES.get(memory.key)

        if template:

            return template.format(

                value=memory.value

            )

        return memory.value

    return None

# ---------------------------------------
# Public API
# ---------------------------------------

def answer(question):

    if not is_personal_question(question):

        return None

    question = question.lower().strip()

    # -----------------------
    # Profile Requests
    # -----------------------

    if (

        "profile" in question

        or "everything about me" in question

        or "what do you know about me" in question

    ):

        return profile_summary()

    return direct_answer(question)
