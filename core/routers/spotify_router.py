def spotify_route(command):

    command = command.lower().strip()

    if command == "open spotify":
        return [{"action": "spotify_open"}]

    if command == "close spotify":
        return [{"action": "spotify_close"}]

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

    if command in [

        "pause spotify",
        "pause music",
        "stop music",
        "stop spotify",

    ]:
        return [{"action": "spotify_pause"}]

    if command in [

        "next song",
        "next music",
        "spotify next",
        "play next song",

    ]:
        return [{"action": "spotify_next"}]

    if command in [

        "previous song",
        "previous music",
        "spotify previous",
        "play previous song",

    ]:
        return [{"action": "spotify_previous"}]

    if command in [

        "volume up spotify",
        "volume up music",

    ]:
        return [{"action": "spotify_volume_up"}]

    if command in [

        "volume down spotify",
        "volume down music",

    ]:
        return [{"action": "spotify_volume_down"}]

    if command.startswith("play "):

        song = command[5:].strip()

        if song.endswith(" on spotify"):
            song = song[:-11].strip()

        if song not in ["spotify", "music"]:

            return [{
                "action": "spotify_play_song",
                "song": song
            }]

    return None