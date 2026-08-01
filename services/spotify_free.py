# """
# JARVIS PRO
# Developer

# Spotify Free Service

# Windows Media Key + URI Automation
# """

# import os
# import time
# import subprocess

# import psutil

# from urllib.parse import quote

# from pynput.keyboard import Controller, Key


# keyboard = Controller()


# # --------------------------------------------------
# # Spotify Process
# # --------------------------------------------------

# def is_running():

#     for process in psutil.process_iter(["name"]):

#         try:

#             if (
#                 process.info["name"]
#                 and process.info["name"].lower() == "spotify.exe"
#             ):
#                 return True

#         except Exception:
#             pass

#     return False


# # --------------------------------------------------
# # Launch Spotify
# # --------------------------------------------------

# def open_spotify():

#     if is_running():
#         return

#     try:
#         os.startfile("spotify:")

#     except Exception:

#         subprocess.Popen(
#             "start spotify:",
#             shell=True
#         )

#     # Wait until Spotify starts

#     for _ in range(30):

#         if is_running():
#             break

#         time.sleep(1)

#     # Give Spotify UI time to load

#     time.sleep(2)


# # --------------------------------------------------
# # Close Spotify
# # --------------------------------------------------

# def close_spotify():

#     os.system(
#         "taskkill /IM Spotify.exe /F >nul 2>&1"
#     )


# # --------------------------------------------------
# # Play / Resume
# # --------------------------------------------------

# def play():

#     open_spotify()

#     time.sleep(1)

#     keyboard.press(Key.media_play_pause)
#     keyboard.release(Key.media_play_pause)


# # --------------------------------------------------
# # Pause
# # --------------------------------------------------

# def pause():

#     keyboard.press(Key.media_play_pause)
#     keyboard.release(Key.media_play_pause)


# # --------------------------------------------------
# # Next
# # --------------------------------------------------

# def next_track():

#     keyboard.press(Key.media_next)
#     keyboard.release(Key.media_next)


# # --------------------------------------------------
# # Previous
# # --------------------------------------------------

# def previous_track():

#     keyboard.press(Key.media_previous)
#     keyboard.release(Key.media_previous)


# # --------------------------------------------------
# # Volume
# # --------------------------------------------------

# def volume_up():

#     keyboard.press(Key.media_volume_up)
#     keyboard.release(Key.media_volume_up)


# def volume_down():

#     keyboard.press(Key.media_volume_down)
#     keyboard.release(Key.media_volume_down)


# # --------------------------------------------------
# # Search Song
# # --------------------------------------------------

# def search(song):

#     open_spotify()

#     song = quote(song)

#     try:

#         os.startfile(
#             f"spotify:search:{song}"
#         )

#     except Exception:

#         pass