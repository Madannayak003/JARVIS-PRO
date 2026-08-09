from core.registry import register
from voice.manager import speak

from skills.browser.browser_controller import browser


# =====================================================
# YouTube Search
# =====================================================

def ai_youtube(data):

    query = data.get("query", "").strip()

    if not query:
        return False

    speak(f"Searching YouTube for {query}")

    browser.search_youtube(query)

    return True


# =====================================================
# YouTube Controls
# =====================================================

def youtube_play_first(data):

    speak("Playing the first video")

    browser.play_first_video()

    return True


def youtube_pause(data):

    speak("Pausing YouTube")

    browser.pause_video()

    return True


def youtube_resume(data):

    speak("Resuming YouTube")

    browser.resume_video()

    return True


def youtube_next(data):

    speak("Playing next video")

    browser.next_video()

    return True


def youtube_previous(data):

    speak("Playing previous video")

    browser.previous_video()

    return True


# =====================================================
# Registry
# =====================================================

register("youtube_automation", ai_youtube)

register("youtube_play_first", youtube_play_first)

register("youtube_pause", youtube_pause)

register("youtube_resume", youtube_resume)

register("youtube_next", youtube_next)

register("youtube_previous", youtube_previous)