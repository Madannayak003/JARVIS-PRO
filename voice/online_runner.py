"""
JARVIS PRO
Online Voice Runner

This is only a wrapper around the existing online JARVIS.

IMPORTANT:
Do not modify the existing online voice architecture.
"""

from core.assistant import run as run_online


def run():
    """
    Start the existing online JARVIS.
    """

    print("[ONLINE VOICE] Starting existing online JARVIS...")

    return run_online()