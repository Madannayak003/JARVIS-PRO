from core.registry import register
from voice.manager import speak

from skills.browser.browser_controller import browser
from config.youtube import get_first_video
from config.youtube import get_video_list

import threading

youtube_queue = []
youtube_index = -1
current_youtube_query = ""

# =====================================================
# YouTube Search
# =====================================================

def ai_youtube(data):

    global current_youtube_query

    query = data.get("query", "").strip()

    if not query:
        return False

    current_youtube_query = query

    speak(f"Searching YouTube for {query}")

    browser.search_youtube(query)

    return True 


# =====================================================
# YouTube Controls
# =====================================================

def youtube_play_first(data):
    
    print(
        f"[YouTube THREAD] "
        f"{threading.current_thread().name} | "
        f"ID: {threading.get_ident()}"
    )

    global youtube_queue, youtube_index, current_youtube_query

    query = data.get("query", "").strip()

    # Use the previous YouTube search if no new query was supplied
    if not query:
        query = current_youtube_query

    if not query:
        speak("What should I play on YouTube?")
        return False

    speak(f"Finding YouTube videos for {query}")

    videos = get_video_list(query, 10)

    if not videos:
        speak("I could not find YouTube videos.")
        return False

    # Save search results as JARVIS queue
    youtube_queue = videos
    youtube_index = 0

    video = youtube_queue[youtube_index]

    print(f"[YouTube Queue] Loaded {len(youtube_queue)} videos")
    print(f"[YouTube Queue] Position: {youtube_index + 1}")
    print(f"[YouTube API] Playing: {video['title']}")
    print(f"[YouTube API] Video ID: {video['video_id']}")

    speak(f"Playing {video['title']}")

    return browser.play_video(video["video_id"])


def youtube_pause(data):

    speak("Pausing YouTube")

    return browser.pause_video()


def youtube_resume(data):

    speak("Resuming YouTube")

    return browser.resume_video()


def youtube_next(data):

    global youtube_queue, youtube_index

    if not youtube_queue:
        speak("There is no YouTube queue.")
        return False

    # Move to next video
    if youtube_index + 1 >= len(youtube_queue):
        speak("There are no more videos in the queue.")
        return False

    youtube_index += 1

    video = youtube_queue[youtube_index]

    print(f"[YouTube Queue] Position: {youtube_index + 1}/{len(youtube_queue)}")
    print(f"[YouTube Queue] Playing: {video['title']}")
    print(f"[YouTube API] Video ID: {video['video_id']}")

    speak(f"Playing {video['title']}")

    return browser.play_video(video["video_id"])


def youtube_previous(data):

    global youtube_queue, youtube_index

    if not youtube_queue:
        speak("There is no YouTube queue.")
        return False

    # Move to previous video
    if youtube_index <= 0:
        speak("This is the first video in the queue.")
        return False

    youtube_index -= 1

    video = youtube_queue[youtube_index]

    print(
        f"[YouTube Queue] Position: "
        f"{youtube_index + 1}/{len(youtube_queue)}"
    )

    print(
        f"[YouTube Queue] Playing: "
        f"{video['title']}"
    )

    print(
        f"[YouTube API] Video ID: "
        f"{video['video_id']}"
    )

    speak(f"Playing {video['title']}")

    return browser.play_video(video["video_id"])


# =====================================================
# Registry
# =====================================================

register("youtube_search", ai_youtube)

register("youtube_play_first", youtube_play_first)

register("youtube_pause", youtube_pause)

register("youtube_resume", youtube_resume)

register("youtube_next", youtube_next)

register("youtube_previous", youtube_previous)