def spotify_route(command):

    command = command.lower().strip()

    # =====================================================
    # Open / Close
    # =====================================================

    if command == "open spotify":
        return [{"action": "spotify_open"}]

    if command == "close spotify":
        return [{"action": "spotify_close"}]

    # =====================================================
    # Play / Resume
    # =====================================================

    if command in [

        "play spotify",
        "play music",
        "play song",
        "resume",
        "resume spotify",
        "resume music",
        "continue music",
        "continue spotify",
        "start music",
        "start spotify",

    ]:
        return [{"action": "spotify_play"}]

    # =====================================================
    # Pause
    # =====================================================

    if command in [

        "pause spotify",
        "pause music",
        "stop music",
        "stop spotify",

    ]:
        return [{"action": "spotify_pause"}]

    # =====================================================
    # Next
    # =====================================================

    if command in [

        "next song",
        "next music",
        "spotify next",
        "play next song",

    ]:
        return [{"action": "spotify_next"}]

    # =====================================================
    # Previous
    # =====================================================

    if command in [

        "previous song",
        "previous music",
        "spotify previous",
        "play previous song",

    ]:
        return [{"action": "spotify_previous"}]

    # =====================================================
    # Spotify Volume Up
    # =====================================================

    if command in [

        "volume up spotify",
        "volume up music",
        "spotify volume up",
        "increase spotify volume",
        "increase music volume",
        "make spotify louder",
        "make music louder",

    ]:
        return [{"action": "spotify_volume_up"}]

    # =====================================================
    # Spotify Volume Down
    # =====================================================

    if command in [

        "volume down spotify",
        "volume down music",
        "spotify volume down",
        "decrease spotify volume",
        "decrease music volume",
        "make spotify quieter",
        "make music quieter",

    ]:
        return [{"action": "spotify_volume_down"}]

    # =====================================================
    # IMPORTANT:
    # YouTube commands must NOT be captured here.
    # =====================================================

    if command in [

        "play first video",
        "play first youtube video",
        "play youtube video",
        "play next video",
        "play the next video",
        "play previous video",
        "play the previous video",

    ]:
        return None

    # =====================================================
    # Play Specific Spotify Song
    # =====================================================

    if command.startswith("play "):

        song = command[5:].strip()

        if song.endswith(" on spotify"):
            song = song[:-11].strip()

        if song not in [
            "spotify",
            "music",
            "song",
            "first video",
            "youtube video",
        ]:

            return [{
                "action": "spotify_play_song",
                "song": song
            }]

    return None