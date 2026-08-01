import sys

from voice.manager import speak
from core.context import set_value


def sleep():

    speak(
        "Entering sleep mode. Say Jarvis to wake me."
    )

    set_value(
        "state",
        "sleep"
    )


def wake():

    speak(
        "Welcome back Sir."
    )

    set_value(
        "state",
        "online"
    )


def shutdown():

    speak(
        "Goodbye Sir."
    )

    sys.exit(0)