import re


def parse_whatsapp(command):

    command = command.strip()

    # -------------------------------------------------
    # Send WhatsApp message
    # -------------------------------------------------

    patterns = [

        # send whatsapp to Ammu saying good night
        r"send\s+whatsapp\s+to\s+(.+?)\s+saying\s+(.+)",

        # send whatsapp message to Ammu good night
        r"send\s+whatsapp\s+message\s+to\s+(.+?)\s+(.+)",

        # send message to Ammu good night
        r"send\s+message\s+to\s+(.+?)\s+(.+)",

        # send whatsapp to Ammu good night
        r"send\s+whatsapp\s+to\s+(.+?)\s+(.+)",

        # message Ammu good night
        r"message\s+(.+?)\s+(.+)",

        # text Ammu good night
        r"text\s+(.+?)\s+(.+)",

        # whatsapp Ammu good night
        r"whatsapp\s+(.+?)\s+(.+)",

        # send Ammu good night
        r"send\s+(.+?)\s+(.+)",

    ]

    for pattern in patterns:

        match = re.fullmatch(
            pattern,
            command,
            re.IGNORECASE
        )

        if match:

            return {

                "contact": match.group(1).strip(),

                "message": match.group(2).strip()

            }

    return None