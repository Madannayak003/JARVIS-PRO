# """
# JARVIS PRO
# Developer

# Spotify Adapter

# Automatically switches between:

# • Spotify Premium API
# • Spotify Free Windows Automation
# """

# from services import spotify_api
# from services import spotify_free


# # --------------------------------------------------
# # Open
# # --------------------------------------------------

# def open():

#     spotify_free.open_spotify()


# # --------------------------------------------------
# # Close
# # --------------------------------------------------

# def close():

#     spotify_free.close_spotify()


# # --------------------------------------------------
# # Play / Resume
# # --------------------------------------------------

# def play():

#     try:

#         if spotify_api.is_premium():

#             return spotify_api.resume_playback()

#     except Exception as e:

#         print("[SPOTIFY PREMIUM]", e)

#     spotify_free.play()

#     return True, "Playing music."

# # --------------------------------------------------
# # Pause
# # --------------------------------------------------

# def pause():

#     if spotify_api.is_premium():

#         try:

#             spotify_api.pause_playback()

#             return True, "Paused."

#         except Exception as e:

#             print("[SPOTIFY PREMIUM]", e)

#     spotify_free.pause()

#     return True, "Paused."


# # --------------------------------------------------
# # Next
# # --------------------------------------------------

# def next_track():

#     if spotify_api.is_premium():

#         try:

#             spotify_api.spotify_client().next_track()

#             return True, "Next."

#         except Exception as e:

#             print("[SPOTIFY PREMIUM]", e)

#     spotify_free.next_track()

#     return True, "Next."


# # --------------------------------------------------
# # Previous
# # --------------------------------------------------

# def previous_track():

#     if spotify_api.is_premium():

#         try:

#             spotify_api.spotify_client().previous_track()

#             return True, "Previous."

#         except Exception as e:

#             print("[SPOTIFY PREMIUM]", e)

#     spotify_free.previous_track()

#     return True, "Previous."


# # --------------------------------------------------
# # Volume
# # --------------------------------------------------

# def volume_up():

#     spotify_free.volume_up()


# def volume_down():

#     spotify_free.volume_down()


# # --------------------------------------------------
# # Play Song
# # --------------------------------------------------

# def play_song(song):

#     if spotify_api.is_premium():

#         try:

#             return spotify_api.play_track(song)

#         except Exception as e:

#             print("[SPOTIFY PREMIUM]", e)

#     spotify_free.search(song)

#     return (
#         True,
#         f"Searching for {song} on Spotify."
#     )


# # --------------------------------------------------
# # Current Song
# # --------------------------------------------------

# def current_song():

#     if spotify_api.is_premium():

#         try:

#             return spotify_api.current_song()

#         except Exception:

#             return None

#     return None