MEDIA = {

    # ---------- Volume ----------

    "volume up": {
        "action": "volume",
        "direction": "up"
    },

    "increase volume": {
        "action": "volume",
        "direction": "up"
    },

    "raise volume": {
        "action": "volume",
        "direction": "up"
    },

    "volume down": {
        "action": "volume",
        "direction": "down"
    },

    "decrease volume": {
        "action": "volume",
        "direction": "down"
    },

    "lower volume": {
        "action": "volume",
        "direction": "down"
    },

    "mute": {
        "action": "volume",
        "direction": "mute"
    },

    "mute volume": {
        "action": "volume",
        "direction": "mute"
    },

    # ---------- Clipboard ----------

    "read clipboard": {
        "action": "clipboard",
        "mode": "read"
    },

    "show clipboard": {
        "action": "clipboard",
        "mode": "read"
    },

    "explain clipboard": {
        "action": "clipboard",
        "mode": "explain"
    },

    "summarize clipboard": {
        "action": "clipboard",
        "mode": "summary"
    },

    # ---------- Screenshot ----------

    "analyze screenshot": {
        "action": "screenshot_ai"
    },

    "describe screenshot": {
        "action": "screenshot_ai"
    }

}


def media_route(command):

    command = command.lower().strip()

    if command in MEDIA:
        return [MEDIA[command]]

    return None