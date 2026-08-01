import re

from services.whatsapp_parser import parse_whatsapp


def whatsapp_route(command):

    command = command.lower().strip()

    # ------------------------
    # Open / Close
    # ------------------------

    if command in ["open whatsapp", "launch whatsapp"]:
        return [{"action": "whatsapp_open"}]

    if command in ["close whatsapp", "exit whatsapp"]:
        return [{"action": "whatsapp_close"}]

    # # ------------------------
    # # Natural message parser
    # # ------------------------

    # result = parse_whatsapp(command)

    # if result:

    #     return [{
    #         "action": "whatsapp_send_message",
    #         "contact": result["contact"],
    #         "message": result["message"]
    #     }]
        
    # ------------------------
    # Ask for Contact
    # ------------------------

    if command in [

        "message",
        "send message",
        "send whatsapp",
        "send whatsapp message"

    ]:

        return [{

            "action": "whatsapp_wait_contact"

        }]

    # ------------------------
    # Conversation mode
    # ------------------------

    if command.startswith("message "):

        contact = command.replace("message", "", 1).strip()

        if contact:

            return [{
                "action": "whatsapp_wait_message",
                "contact": contact
            }]

    if command.startswith("tell "):

        contact = command.replace("tell", "", 1).strip()

        if contact:

            return [{
                "action": "whatsapp_wait_message",
                "contact": contact
            }]

    if command.startswith("text "):

        contact = command.replace("text", "", 1).strip()

        if contact:

            return [{
                "action": "whatsapp_wait_message",
                "contact": contact
            }]

    if command.startswith("send whatsapp to "):

        contact = command.replace("send whatsapp to", "", 1).strip()

        if contact:

            return [{
                "action": "whatsapp_wait_message",
                "contact": contact
            }]
            
            
    match = re.fullmatch(

        r"(?:send|share)\s+(?:the\s+)?(?:latest|last)\s+(?:photo|picture|image)\s+(?:to|with)\s+(.+)",

        command,

        re.IGNORECASE

    )

    if match:

        return [

            {

                "action": "whatsapp_send_latest_photo",

                "contact": match.group(1).strip()

            }

        ]
        
    match = re.fullmatch(

    r"(?:send|share)\s+(?:the\s+)?(?:latest|last)\s+screenshot\s+(?:to|with)\s+(.+)",

    command,

    re.IGNORECASE

    )

    if match:

        return [

            {

                "action": "whatsapp_send_latest_screenshot",

                "contact": match.group(1).strip()

            }

        ]
        
    match = re.fullmatch(

    r"send\s+(.+?)\s+to\s+(.+)",

    command,

    re.IGNORECASE

    )

    if match:

        filename = match.group(1).strip()

        contact = match.group(2).strip()

        # Skip if it's a text message
        if not filename.startswith("message"):

            return [

                {

                    "action": "whatsapp_send_file",

                    "filename": filename,

                    "contact": contact

                }

            ]

    # ------------------------
    # Natural message parser
    # ------------------------

    result = parse_whatsapp(command)

    if result:

        return [{
            "action": "whatsapp_send_message",
            "contact": result["contact"],
            "message": result["message"]
        }]

    return None