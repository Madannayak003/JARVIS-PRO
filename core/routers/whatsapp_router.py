import re

from services.whatsapp_parser import parse_whatsapp


def whatsapp_route(command):

    command = command.lower().strip()

    # -------------------------------------------------
    # Open / Close
    # -------------------------------------------------

    if command in [
        "open whatsapp",
        "launch whatsapp"
    ]:

        return [
            {
                "action": "whatsapp_open"
            }
        ]

    if command in [
        "close whatsapp",
        "exit whatsapp"
    ]:

        return [
            {
                "action": "whatsapp_close"
            }
        ]

    # -------------------------------------------------
    # Ask for Contact
    # -------------------------------------------------

    if command in [

        "message",
        "send message",
        "send whatsapp",
        "send whatsapp message"

    ]:

        return [
            {
                "action": "whatsapp_wait_contact"
            }
        ]

    # -------------------------------------------------
    # Latest Photo
    # -------------------------------------------------

    match = re.fullmatch(

        r"(?:send|share)\s+"
        r"(?:the\s+)?"
        r"(?:latest|last)\s+"
        r"(?:photo|picture|image)\s+"
        r"(?:to|with)\s+(.+)",

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

    # -------------------------------------------------
    # Latest Screenshot
    # -------------------------------------------------

    match = re.fullmatch(

        r"(?:send|share)\s+"
        r"(?:the\s+)?"
        r"(?:latest|last)\s+"
        r"screenshot\s+"
        r"(?:to|with)\s+(.+)",

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

    # -------------------------------------------------
    # Natural WhatsApp Message
    # -------------------------------------------------
    #
    # IMPORTANT:
    # This MUST come before the generic file matcher.
    #

    result = parse_whatsapp(command)

    if result:

        return [
            {
                "action": "whatsapp_send_message",

                "contact": result["contact"],

                "message": result["message"]
            }
        ]

    # -------------------------------------------------
    # Conversation Mode
    # -------------------------------------------------

    if command.startswith("message "):

        contact = command.replace(
            "message",
            "",
            1
        ).strip()

        if contact:

            return [
                {
                    "action": "whatsapp_wait_message",

                    "contact": contact
                }
            ]

    if command.startswith("tell "):

        contact = command.replace(
            "tell",
            "",
            1
        ).strip()

        if contact:

            return [
                {
                    "action": "whatsapp_wait_message",

                    "contact": contact
                }
            ]

    if command.startswith("text "):

        contact = command.replace(
            "text",
            "",
            1
        ).strip()

        if contact:

            return [
                {
                    "action": "whatsapp_wait_message",

                    "contact": contact
                }
            ]

    # -------------------------------------------------
    # Send WhatsApp To Contact
    # -------------------------------------------------
    #
    # Example:
    # "send whatsapp to ammu"
    #
    # This is only reached when parse_whatsapp()
    # did NOT find a message.
    #

    if command.startswith("send whatsapp to "):

        contact = command.replace(
            "send whatsapp to",
            "",
            1
        ).strip()

        if contact:

            return [
                {
                    "action": "whatsapp_wait_message",

                    "contact": contact
                }
            ]

    # -------------------------------------------------
    # Send File
    # -------------------------------------------------

    match = re.fullmatch(

        r"send\s+(.+?)\s+to\s+(.+)",

        command,

        re.IGNORECASE

    )

    if match:

        filename = match.group(1).strip()

        contact = match.group(2).strip()

        # Prevent obvious message commands
        if filename.lower() not in [

            "message",
            "whatsapp",
            "whatsapp message"

        ]:

            return [
                {
                    "action": "whatsapp_send_file",

                    "filename": filename,

                    "contact": contact
                }
            ]

    return None