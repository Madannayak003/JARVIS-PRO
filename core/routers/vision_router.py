import re


VISION = {

    # =================================================
    # Camera
    # =================================================

    "take photo": {
        "action": "capture"
    },

    "take a photo": {
        "action": "capture"
    },

    "take picture": {
        "action": "capture"
    },

    "take a picture": {
        "action": "capture"
    },

    "capture image": {
        "action": "capture"
    },

    "open camera": {
        "action": "camera_preview"
    },

    "start camera": {
        "action": "camera_preview"
    },

    "close camera": {
        "action": "camera_close"
    },

    "stop camera": {
        "action": "camera_close"
    },

    # =================================================
    # Recording
    # =================================================

    "start recording": {
        "action": "start_recording"
    },

    "record video": {
        "action": "start_recording"
    },

    "record": {
        "action": "start_recording"
    },

    "stop recording": {
        "action": "stop_recording"
    },

    "stop video": {
        "action": "stop_recording"
    },

    # =================================================
    # Camera Status
    # =================================================

    "camera status": {
        "action": "camera_status"
    },

    "is camera open": {
        "action": "camera_status"
    },

    # =================================================
    # Vision Start / Stop
    # =================================================

    "start vision": {
        "action": "vision_start"
    },

    "start computer vision": {
        "action": "vision_start"
    },

    "enable vision": {
        "action": "vision_start"
    },

    "stop vision": {
        "action": "vision_stop"
    },

    "stop computer vision": {
        "action": "vision_stop"
    },

    "disable vision": {
        "action": "vision_stop"
    },

    # =================================================
    # Vision Description
    # =================================================

    "what do you see": {
        "action": "vision_describe"
    },

    "what can you see": {
        "action": "vision_describe"
    },

    "describe what you see": {
        "action": "vision_describe"
    },

    "describe the scene": {
        "action": "vision_describe"
    },

    "describe the camera": {
        "action": "vision_describe"
    },

    "describe the view": {
        "action": "vision_describe"
    },

    "what is in front of me": {
        "action": "vision_describe"
    },

    # =================================================
    # Vision Position
    # =================================================

    "what is in the center": {
        "action": "vision_position",
        "position": "center"
    },

    "what is in center": {
        "action": "vision_position",
        "position": "center"
    },

    "what is in the middle": {
        "action": "vision_position",
        "position": "center"
    },

    "what is on the left": {
        "action": "vision_position",
        "position": "left"
    },

    "what is on my left": {
        "action": "vision_position",
        "position": "left"
    },

    "what is on the right": {
        "action": "vision_position",
        "position": "right"
    },

    "what is on my right": {
        "action": "vision_position",
        "position": "right"
    },

}


def vision_route(command):

    command = command.lower().strip()

    # =================================================
    # 1. Exact static match
    # =================================================

    if command in VISION:

        return [
            VISION[command]
        ]

    # =================================================
    # 2. Dynamic object count
    #
    # Examples:
    # "how many people are there"
    # "how many persons"
    # "how many cars"
    # "how many bottles do you see"
    # =================================================

    match = re.fullmatch(
        r"how many (.+?)(?: are there| do you see| can you see)?",
        command,
        re.IGNORECASE,
    )

    if match:

        object_name = match.group(1).strip()

        if object_name:

            # Normalize common object names
            aliases = {
                "people": "person",
                "persons": "person",
                "phones": "cell phone",
                "cellphones": "cell phone",
                "cell phones": "cell phone",
                "mobile": "cell phone",
                "mobiles": "cell phone",
                "mobile phones": "cell phone",
                "cars": "car",
                "bikes": "bicycle",
                "bicycles": "bicycle",
                "dogs": "dog",
                "cats": "cat",
            }

            object_name = aliases.get(
                object_name,
                object_name
            )

            return [
                {
                    "action": "vision_count",
                    "object": object_name,
                }
            ]

    # =================================================
    # 3. Dynamic object existence
    #
    # Examples:
    # "is there a phone"
    # "is there a person"
    # "do you see a phone"
    # "can you see a car"
    # =================================================

    match = re.fullmatch(
        r"(?:is there|do you see|can you see)\s+(?:a|an|the)?\s*(.+?)(?:\?|)?",
        command,
        re.IGNORECASE,
    )

    if match:

        object_name = match.group(1).strip()

        if object_name:

            aliases = {
                "people": "person",
                "persons": "person",
                "phone": "cell phone",
                "phones": "cell phone",
                "cellphone": "cell phone",
                "cellphones": "cell phone",
                "mobile": "cell phone",
                "mobile phone": "cell phone",
                "mobiles": "cell phone",
                "car": "car",
                "cars": "car",
                "bike": "bicycle",
                "bikes": "bicycle",
            }

            object_name = aliases.get(
                object_name,
                object_name
            )

            return [
                {
                    "action": "vision_check",
                    "object": object_name,
                }
            ]

    # =================================================
    # 4. Dynamic position
    # =================================================

    position_patterns = {

        "left": [
            "what is on the left",
            "what is on my left",
            "what's on the left",
            "what's on my left",
            "what do you see on the left",
            "what do you see on my left",
        ],

        "center": [
            "what is in the center",
            "what is in center",
            "what is in the middle",
            "what's in the center",
            "what's in center",
            "what's in the middle",
            "what do you see in the center",
            "what do you see in the middle",
        ],

        "right": [
            "what is on the right",
            "what is on my right",
            "what's on the right",
            "what's on my right",
            "what do you see on the right",
            "what do you see on my right",
        ],
    }

    for position, phrases in position_patterns.items():

        for phrase in phrases:

            if command == phrase:

                return [
                    {
                        "action": "vision_position",
                        "position": position,
                    }
                ]

    # =================================================
    # 5. Phrase matching for static commands
    # =================================================

    for key in sorted(
        VISION.keys(),
        key=len,
        reverse=True
    ):

        if key in command:

            return [
                VISION[key]
            ]

    # =================================================
    # No Vision match
    # =================================================

    return None