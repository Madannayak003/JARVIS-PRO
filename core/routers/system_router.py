SYSTEM = {

    "shutdown":{
        "action":"shutdown"
    },

    "restart":{
        "action":"restart"
    },

    "sleep":{
        "action":"sleep"
    },

    "lock":{
        "action":"lock"
    },

    "battery":{
        "action":"battery"
    },

    "battery status":{
        "action":"battery"
    },
    
    "show battery":{
        "action":"battery"
    },
    
    "show battery status":{
        "action":"battery"
    },

    "brightness up":{
        "action":"brightness",
        "direction":"up"
    },

    "brightness down":{
        "action":"brightness",
        "direction":"down"
    },

    "increase brightness":{
        "action":"brightness",
        "direction":"up"
    },

    "decrease brightness":{
        "action":"brightness",
        "direction":"down"
    },
    
    "increase volume":{
        "action":"volume",
        "direction":"up"
    },
    
    "decrease volume":{
        "action":"volume",
        "direction":"down"
    },

    "screenshot":{
        "action":"screenshot"
    },

    "take screenshot":{
        "action":"screenshot"
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
    }
}


def system_route(command):

    command = command.lower().strip()

    # ---------- Lock ----------

    if command in [
        "lock",
        "lock computer",
        "lock pc",
        "lock laptop",
        "lock screen"
    ]:
        return [{"action": "lock"}]

    # ---------- Shutdown ----------

    if command in [
        "shutdown",
        "shutdown computer",
        "shutdown pc"
    ]:
        return [{"action": "shutdown"}]

    # ---------- Restart ----------

    if command in [
        "restart",
        "restart computer",
        "restart pc"
    ]:
        return [{"action": "restart"}]

    # ---------- Sleep ----------

    if command in [
        "sleep",
        "sleep computer",
        "sleep pc"
    ]:
        return [{"action": "sleep"}]

    if command in SYSTEM:
        return [SYSTEM[command]]

    return None