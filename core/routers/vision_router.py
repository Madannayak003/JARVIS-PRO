VISION = {

    "take photo":{
        "action":"capture"
    },
    
    "take a photo":{
        "action":"capture"
    },

    "take picture":{
        "action":"capture"
    },
    
    "take a picture":{
        "action":"capture"
    },

    "capture image":{
        "action":"capture"
    },

    "open camera":{
        "action":"camera_preview"
    },

    "start camera":{
        "action":"camera_preview"
    },

    "close camera":{
        "action":"camera_close"
    },

    "stop camera":{
        "action":"camera_close"
    },
    
    "start recording": {
        "action":"start_recording"
    },

    "record video": {
        "action":"start_recording"
    },

    "record": {
        "action":"start_recording"
    },

    "stop recording": {
        "action":"stop_recording"
    },

    "stop video": {
        "action":"stop_recording"
    },
    
    "camera status":{
        "action":"camera_status"
    },

    "is camera open":{
        "action":"camera_status"
    },
}


def vision_route(command):

    command = command.lower().strip()

    # 1. Exact match first
    if command in VISION:
        return [VISION[command]]

    # 2. Longest phrase first
    for key in sorted(VISION.keys(), key=len, reverse=True):

        if key in command:

            return [VISION[key]]

    return None