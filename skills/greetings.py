import random
from datetime import datetime

from core.registry import register
from voice.manager import speak


# ----------------------------------------------------------
# General Greetings
# ----------------------------------------------------------

GREETINGS = [
    "Hello.",
    "Hi there.",
    "Hey.",
    "Welcome back.",
    "Nice to see you again.",
    "At your service.",
    "Ready whenever you are.",
    "How can I help you?",
    "What can I do for you today?",
    "Awaiting your command."
]


HOW_ARE_YOU = [
    "I'm doing great. Thanks for asking.",
    "Everything is running smoothly.",
    "All systems are operational.",
    "I'm functioning perfectly.",
    "Always ready to assist."
]


WELCOME = [
    "You're welcome.",
    "Happy to help.",
    "Anytime.",
    "My pleasure.",
    "Glad I could help."
]


BYE = [
    "Goodbye.",
    "See you later.",
    "Take care.",
    "Have a great day.",
    "See you soon."
]


# ----------------------------------------------------------
# Startup Greeting
# ----------------------------------------------------------

STARTUP = {

    "morning": [

        "Hope you slept well.",
        "Nice to see you again.",
        "Ready whenever you are.",
        "Everything is ready.",
        "How may I assist you today?",
        "Hope today goes well for you.",
        "What are we working on today?",
        "I'm online and ready to help.",
        "All systems are operational.",
        "Looking forward to another productive day."

    ],

    "afternoon": [

        "Welcome back.",
        "Hope your day's going well.",
        "Ready whenever you need me.",
        "Everything is ready.",
        "What shall we work on today?",
        "I'm online and ready.",
        "How can I help you?",
        "Let's get started.",
        "Nice to see you again.",
        "Awaiting your command."

    ],

    "evening": [

        "Welcome back.",
        "Hope you had a good day.",
        "Everything is ready whenever you are.",
        "What shall we work on tonight?",
        "I'm online and ready.",
        "Nice to see you again.",
        "How can I assist you this evening?",
        "Ready whenever you are.",
        "Let's get to work.",
        "Awaiting your command."

    ],

    "night": [

        "Working late tonight?",
        "Still awake? I'm here if you need me.",
        "Ready whenever you are.",
        "Looks like another late session.",
        "Let's get started.",
        "Everything is ready.",
        "I'm online whenever you need assistance.",
        "Hope everything's going well.",
        "How can I help tonight?",
        "Ready for whatever comes next."

    ]

}


def startup_greeting():

    hour = datetime.now().hour

    if 5 <= hour < 12:

        prefix = "Good morning."

        key = "morning"

    elif 12 <= hour < 17:

        prefix = "Good afternoon."

        key = "afternoon"

    elif 17 <= hour < 22:

        prefix = "Good evening."

        key = "evening"

    else:

        prefix = "Good evening."

        key = "night"

    return f"{prefix} {random.choice(STARTUP[key])}"

# ----------------------------------------------------------
# Skills
# ----------------------------------------------------------

def greet(data):

    command = data.get("command", "").lower()

    if command.startswith("good morning"):
        speak("Good morning.")
        return True

    if command.startswith("good afternoon"):
        speak("Good afternoon.")
        return True

    if command.startswith("good evening"):
        speak("Good evening.")
        return True

    speak(random.choice(GREETINGS))
    return True


def how_are_you(data):

    speak(random.choice(HOW_ARE_YOU))
    return True


def welcome(data):

    speak(random.choice(WELCOME))
    return True


def goodbye(data):

    speak(random.choice(BYE))
    return True


register("greet", greet)
register("how_are_you", how_are_you)
register("welcome", welcome)
register("goodbye", goodbye)