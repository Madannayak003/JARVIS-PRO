def greeting_route(command):

    command = command.lower().strip()

    if command in [

        "hello",
        "hi",
        "hey",

        "hello jarvis",
        "hi jarvis",
        "hey jarvis",

        "hello astra",
        "hi astra",
        "hey astra",

        "jarvis hello",
        "jarvis hi",
        "jarvis hey",

        "astra hello",
        "astra hi",
        "astra hey",

        "good morning",
        "good afternoon",
        "good evening",

        "good morning jarvis",
        "good afternoon jarvis",
        "good evening jarvis",

        "good morning astra",
        "good afternoon astra",
        "good evening astra",

        "jarvis good morning",
        "jarvis good afternoon",
        "jarvis good evening",

        "astra good morning",
        "astra good afternoon",
        "astra good evening",

        "good to see you",
        "good to see you jarvis",
        "good to see you astra"

    ]:

        return [{
            "action": "greet",
            "command": command
        }]

    if command in [

        "how are you",
        "how are you jarvis",
        "jarvis how are you",
        "how are you astra",
        "astra how are you"

    ]:

        return [{
            "action": "how_are_you"
        }]

    if command in [

        "thanks",
        "thank you",

        "thanks jarvis",
        "thank you jarvis",

        "thanks astra",
        "thank you astra",

        "jarvis thanks",
        "jarvis thank you",

        "astra thanks",
        "astra thank you"

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

        "bye astra",
        "goodbye astra",
        "see you astra",

        "jarvis bye",
        "jarvis goodbye",

        "astra bye",
        "astra goodbye"

    ]:

        return [{
            "action": "goodbye"
        }]

    return None
