from core.registry import register
from voice.manager import speak

from skills.browser_controller import browser


def ai_youtube(data):

    query = data["query"]

    speak(f"Searching YouTube for {query}")

    browser.search_youtube(query)

    return True


register("youtube_automation", ai_youtube)