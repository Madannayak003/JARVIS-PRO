from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from voice.manager import speak
from core.registry import register


devices = AudioUtilities.GetSpeakers()

interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(interface, POINTER(IAudioEndpointVolume))


def current():

    return int(volume.GetMasterVolumeLevelScalar() * 100)


def set_volume(percent):

    percent = max(0, min(100, int(percent)))

    volume.SetMasterVolumeLevelScalar(
        percent / 100,
        None
    )


def ai_volume(data):

    direction = data.get("direction", "")
    percent = data.get("percent")

    # ---------- Set Volume ----------

    if percent is not None:

        set_volume(percent)

        speak(f"Volume set to {percent} percent")

        return True

    # ---------- Increase ----------

    if direction == "up":

        new = min(100, current() + 10)

        set_volume(new)

        speak(f"Volume {new} percent")

        return True

    # ---------- Decrease ----------

    if direction == "down":

        new = max(0, current() - 5)

        set_volume(new)

        speak(f"Volume {new} percent")

        return True

    # ---------- Mute ----------

    if direction == "mute":

        volume.SetMute(1, None)

        speak("Muted")

        return True

    # ---------- Unmute ----------

    if direction == "unmute":

        volume.SetMute(0, None)

        speak("Unmuted")

        return True

    return False


register("volume", ai_volume)