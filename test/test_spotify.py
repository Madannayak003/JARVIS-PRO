import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from core.voice import speak
from services.spotify_api import play_track

#print(play_track("monica"))

player = play_track("monica(from \"coolie\")")

#print(play_track("shape of you (from \"ed sheeran\")"))

speak("Playing your song on Spotify. Enjoy!")