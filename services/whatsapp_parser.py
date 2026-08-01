import re


def parse_whatsapp(command):

    command = command.strip()

    patterns = [

        r"send whatsapp to (.+?) saying (.+)",

        r"send whatsapp to (.+?) (.+)",
        
        r"send message to (.+?) (.+)",
        
        r"send whatsapp message to (.+?) (.+?)",

        r"message (.+?) (.+)",

        r"tell (.+?) (.+)",

        r"text (.+?) (.+)",

        r"whatsapp (.+?) (.+)",

        r"send (.+?) (.+)"
        
    ]

    for pattern in patterns:

        match = re.fullmatch(pattern, command, re.I)

        if match:

            return {

                "contact": match.group(1).strip(),

                "message": match.group(2).strip()

            }

    return None