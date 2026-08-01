def greeting_route(command):

    command = command.lower().strip()

    if command in [

        "hello",
        "hi",
        "hey",

        "hello jarvis",
        "hi jarvis",
        "hey jarvis",

        "jarvis hello",
        "jarvis hi",
        "jarvis hey",

        "good morning",
        "good afternoon",
        "good evening",

        "good morning jarvis",
        "good afternoon jarvis",
        "good evening jarvis",

        "jarvis good morning",
        "jarvis good afternoon",
        "jarvis good evening",

        "good to see you",
        "good to see you jarvis"

    ]:

        return [{
            "action": "greet",
            "command": command
        }]

    if command in [

        "how are you",
        "how are you jarvis",
        "jarvis how are you"

    ]:

        return [{
            "action": "how_are_you"
        }]

    if command in [

        "thanks",
        "thank you",

        "thanks jarvis",
        "thank you jarvis",

        "jarvis thanks",
        "jarvis thank you"

    ]:

        return [{
            "action": "welcome"
        }]

    if command in [

        "bye",
        "goodbye",
        "see you",

        "bye jarvis",
        "goodbye jarvis",
        "see you jarvis",

        "jarvis bye",
        "jarvis goodbye"

    ]:

        return [{
            "action": "goodbye"
        }]

    return None