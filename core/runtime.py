from core.interrupt import interrupt

INTERRUPTS = {

    "stop",
    
    "stop chart",

    "jarvis stop",

    "cancel",

    "abort",

    "never mind",

    "exit chat",

    "stop chatting",
    
    "stop conversation",
    
    "jarvis stop conversation",

}

def handle_priority(command):

    command = command.lower().strip()

    if command in INTERRUPTS:

        interrupt()

        return True

    return False