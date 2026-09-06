SYSTEM = {

    # ---------------------------------------------------------
    # JARVIS APPLICATION SHUTDOWN
    # ---------------------------------------------------------

    "shutdown": {
        "action": "terminate_jarvis"
    },

    "terminate": {
        "action": "terminate_jarvis"
    },

    "go terminate": {
        "action": "terminate_jarvis"
    },

    "close jarvis": {
        "action": "terminate_jarvis"
    },

    "exit jarvis": {
        "action": "terminate_jarvis"
    },

    "quit jarvis": {
        "action": "terminate_jarvis"
    },

    # ---------------------------------------------------------
    # SYSTEM ACTIONS
    # ---------------------------------------------------------

    "restart": {
        "action": "restart"
    },

    "sleep": {
        "action": "sleep"
    },

    "lock": {
        "action": "lock"
    },

    "battery": {
        "action": "battery"
    },

    "battery status": {
        "action": "battery"
    },

    "show battery": {
        "action": "battery"
    },

    "show battery status": {
        "action": "battery"
    },

    "brightness up": {
        "action": "brightness",
        "direction": "up"
    },

    "brightness down": {
        "action": "brightness",
        "direction": "down"
    },

    "increase brightness": {
        "action": "brightness",
        "direction": "up"
    },

    "decrease brightness": {
        "action": "brightness",
        "direction": "down"
    },

    "increase volume": {
        "action": "volume",
        "direction": "up"
    },

    "decrease volume": {
        "action": "volume",
        "direction": "down"
    },

    "screenshot": {
        "action": "screenshot"
    },

    "take screenshot": {
        "action": "screenshot"
    },

    "time": {
        "action": "time"
    },

    "what time is it": {
        "action": "time"
    },

    "current time": {
        "action": "time"
    },

    "date": {
        "action": "date"
    },

    "start live conversation": {
        "action": "start_live_conversation"
    },

    "start live": {
        "action": "start_live_conversation"
    },

    "stop live conversation": {
        "action": "stop_live_conversation"
    },

    "stop live": {
        "action": "stop_live_conversation"
    },

    "live conversation status": {
        "action": "live_conversation_status"
    },
}


def system_route(command):

    command = command.lower().strip()

    # ---------- Lock ----------

    if command in [
        "lock",
        "lock computer",
        "lock pc",
        "lock laptop",
        "lock screen",
    ]:
        return [{"action": "lock"}]

    # ---------- Windows Shutdown ----------

    if command in [
        "shutdown computer",
        "shutdown pc",
        "shutdown system",
        "shut down computer",
        "shut down system",
        "power off computer",
        "power off system",
    ]:
        return [{"action": "shutdown"}]

    # ---------- Restart ----------

    if command in [
        "restart",
        "restart computer",
        "restart pc",
    ]:
        return [{"action": "restart"}]

    # ---------- Sleep ----------

    if command in [
        "sleep",
        "sleep computer",
        "sleep pc",
    ]:
        return [{"action": "sleep"}]

    # ---------- Exact system commands ----------

    if command in SYSTEM:
        return [SYSTEM[command]]

    return None