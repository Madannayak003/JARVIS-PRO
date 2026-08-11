import re


# =========================================================
# JARVIS PRO
# Vision Router
#
# Three independent domains:
#
#   1. CAMERA
#   2. YOLO VISION
#   3. SCREEN VISION
#
# This router ONLY decides which action to execute.
# It does NOT start/stop engines directly.
# =========================================================


# =========================================================
# CAMERA COMMANDS
# =========================================================

CAMERA_COMMANDS = {

    # -----------------------------------------------------
    # Photo
    # -----------------------------------------------------

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

    "capture photo": {
        "action": "capture"
    },

    # -----------------------------------------------------
    # Camera Preview
    # -----------------------------------------------------

    "open camera": {
        "action": "camera_preview"
    },

    "start camera": {
        "action": "camera_preview"
    },

    "show camera": {
        "action": "camera_preview"
    },

    "camera preview": {
        "action": "camera_preview"
    },

    # -----------------------------------------------------
    # Camera Close
    # -----------------------------------------------------

    "close camera": {
        "action": "camera_close"
    },

    "stop camera": {
        "action": "camera_close"
    },

    "turn off camera": {
        "action": "camera_close"
    },

    # -----------------------------------------------------
    # Recording
    # -----------------------------------------------------

    "start recording": {
        "action": "start_recording"
    },

    "record video": {
        "action": "start_recording"
    },

    "record": {
        "action": "start_recording"
    },

    "start video recording": {
        "action": "start_recording"
    },

    "stop recording": {
        "action": "stop_recording"
    },

    "stop video": {
        "action": "stop_recording"
    },

    "stop video recording": {
        "action": "stop_recording"
    },

    # -----------------------------------------------------
    # Camera Status
    # -----------------------------------------------------

    "camera status": {
        "action": "camera_status"
    },

    "is camera open": {
        "action": "camera_status"
    },

    "is the camera open": {
        "action": "camera_status"
    },

}


# =========================================================
# YOLO VISION COMMANDS
# =========================================================

YOLO_VISION_COMMANDS = {

    # -----------------------------------------------------
    # Scene Description
    # -----------------------------------------------------

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

    "look around": {
        "action": "vision_describe"
    },

    "analyze the scene": {
        "action": "vision_describe"
    },

    # -----------------------------------------------------
    # Position
    # -----------------------------------------------------

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


# =========================================================
# SCREEN VISION COMMANDS
# =========================================================

SCREEN_VISION_COMMANDS = {

    "what am i looking at": {
        "action": "screen_vision_analyze"
    },

    "what is on my screen": {
        "action": "screen_vision_analyze"
    },

    "what's on my screen": {
        "action": "screen_vision_analyze"
    },

    "what do you see on my screen": {
        "action": "screen_vision_analyze"
    },

    "describe my screen": {
        "action": "screen_vision_analyze"
    },

    "describe the screen": {
        "action": "screen_vision_analyze"
    },

    "analyze my screen": {
        "action": "screen_vision_analyze"
    },

    "analyze the screen": {
        "action": "screen_vision_analyze"
    },

    "look at my screen": {
        "action": "screen_vision_analyze"
    },

    "what is showing on my screen": {
        "action": "screen_vision_analyze"
    },

    "what is displayed on my screen": {
        "action": "screen_vision_analyze"
    },

    "read my screen": {
        "action": "screen_vision_analyze"
    },

}


# =========================================================
# YOLO OBJECT ALIASES
# =========================================================

OBJECT_ALIASES = {

    "people": "person",
    "persons": "person",

    "phones": "cell phone",
    "phone": "cell phone",
    "cellphone": "cell phone",
    "cellphones": "cell phone",
    "cell phones": "cell phone",
    "mobile": "cell phone",
    "mobiles": "cell phone",
    "mobile phone": "cell phone",
    "mobile phones": "cell phone",

    "cars": "car",

    "bikes": "bicycle",
    "bike": "bicycle",
    "bicycles": "bicycle",

    "dogs": "dog",
    "cats": "cat",
}


# =========================================================
# POSITION PATTERNS
# =========================================================

POSITION_PATTERNS = {

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


# =========================================================
# NORMALIZE OBJECT
# =========================================================

def _normalize_object(object_name):

    object_name = object_name.strip().lower()

    return OBJECT_ALIASES.get(
        object_name,
        object_name
    )


# =========================================================
# YOLO OBJECT COUNT
#
# Examples:
#
#   how many people
#   how many cars are there
#   how many bottles do you see
# =========================================================

def _match_object_count(command):

    match = re.fullmatch(
        r"how many (.+?)(?: are there| do you see| can you see)?",
        command,
        re.IGNORECASE,
    )

    if not match:

        return None

    object_name = match.group(1).strip()

    if not object_name:

        return None

    object_name = _normalize_object(
        object_name
    )

    return {
        "action": "vision_count",
        "object": object_name,
    }


# =========================================================
# YOLO OBJECT EXISTENCE
#
# Examples:
#
#   is there a person
#   do you see a phone
#   can you see a car
# =========================================================

def _match_object_existence(command):

    match = re.fullmatch(
        r"(?:is there|do you see|can you see)"
        r"\s+(?:a|an|the)?\s*(.+?)(?:\?)?",
        command,
        re.IGNORECASE,
    )

    if not match:

        return None

    object_name = match.group(1).strip()

    if not object_name:

        return None

    object_name = _normalize_object(
        object_name
    )

    return {
        "action": "vision_check",
        "object": object_name,
    }


# =========================================================
# YOLO POSITION
# =========================================================

def _match_position(command):

    for position, phrases in POSITION_PATTERNS.items():

        for phrase in phrases:

            if command == phrase:

                return {
                    "action": "vision_position",
                    "position": position,
                }

    return None


# =========================================================
# STATIC COMMAND MATCHER
# =========================================================

def _match_static(command, commands):

    # Exact match first.

    if command in commands:

        return commands[command]

    # Longer phrases first.
    # Prevents a shorter phrase from winning
    # when a more specific phrase exists.

    for key in sorted(
        commands.keys(),
        key=len,
        reverse=True
    ):

        if key in command:

            return commands[key]

    return None


# =========================================================
# MAIN VISION ROUTER
# =========================================================

def vision_route(command):

    if not command:

        return None

    command = command.lower().strip()

    # =====================================================
    # 1. CAMERA
    # =====================================================

    plan = _match_static(
        command,
        CAMERA_COMMANDS
    )

    if plan:

        return [plan]

    # =====================================================
    # 2. SCREEN VISION
    #
    # IMPORTANT:
    # Check screen vision BEFORE generic YOLO phrases.
    #
    # Example:
    #
    # "what do you see on my screen"
    #
    # must never become:
    #
    # vision_describe
    # =====================================================

    plan = _match_static(
        command,
        SCREEN_VISION_COMMANDS
    )

    if plan:

        return [plan]

    # =====================================================
    # 3. YOLO OBJECT COUNT
    # =====================================================

    plan = _match_object_count(
        command
    )

    if plan:

        return [plan]

    # =====================================================
    # 4. YOLO OBJECT EXISTENCE
    # =====================================================

    plan = _match_object_existence(
        command
    )

    if plan:

        return [plan]

    # =====================================================
    # 5. YOLO POSITION
    # =====================================================

    plan = _match_position(
        command
    )

    if plan:

        return [plan]

    # =====================================================
    # 6. YOLO SCENE DESCRIPTION
    # =====================================================

    plan = _match_static(
        command,
        YOLO_VISION_COMMANDS
    )

    if plan:

        return [plan]

    # =====================================================
    # No Vision Match
    # =====================================================

    return None