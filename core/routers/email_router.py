import re


def email_route(command):

    command = command.strip()

    # -------------------------------------------------
    # Send Email
    # -------------------------------------------------

    match = re.fullmatch(

        r"(?:send|write|compose)\s+(?:an?\s+)?email\s+to\s+(.+)",

        command,

        re.IGNORECASE

    )

    if match:

        recipient = match.group(1).strip()

        if recipient:

            return [

                {

                    "action": "send_email",

                    "recipient": recipient

                }

            ]

    # -------------------------------------------------
    # Open Gmail
    # -------------------------------------------------

    if command.lower() in [

        "open gmail",

        "gmail",

        "open email",

        "open mail"

    ]:

        return [

            {

                "action": "gmail_open"

            }

        ]

    return None