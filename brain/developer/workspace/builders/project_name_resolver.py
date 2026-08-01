"""
JARVIS PRO
Developer Workspace

Project Name Resolver
"""

import re
from pathlib import Path

from brain.developer.generator.models.generated_project import (
    GeneratedProject,
)


class ProjectNameResolver:
    """
    Generates a unique project name.
    """

    DEFAULT_NAME = "GeneratedProject"
    
    SPECIAL_WORDS = {

        "rfid": "RFID",
        "iot": "IoT",
        "api": "API",
        "gps": "GPS",
        "gsm": "GSM",
        "wifi": "WiFi",
        "bluetooth": "Bluetooth",
        "esp32": "ESP32",
        "esp8266": "ESP8266",
        "arduino": "Arduino",
        "mqtt": "MQTT",
        "http": "HTTP",
        "https": "HTTPS",
        "oled": "OLED",
        "lcd": "LCD",
        "i2c": "I2C",
        "spi": "SPI",
        "uart": "UART",
        "usb": "USB",
        "json": "JSON",
        "html": "HTML",
        "css": "CSS",
        "javascript": "JavaScript",

    }

    def resolve(
        self,
        project: GeneratedProject,
        output_directory: Path,
    ) -> str:

        # -------------------------------
        # Existing Project Name
        # -------------------------------

        if project.name:

            words = re.findall(r"[A-Za-z0-9]+", project.name)

            parts = []

            for word in words:

                key = word.lower()

                if key in self.SPECIAL_WORDS:

                    parts.append(self.SPECIAL_WORDS[key])

                else:

                    parts.append(word.capitalize())

            base_name = "".join(parts)

        else:

            text = project.user_request.strip()

            # ---------------------------------
            # Remove common command words
            # ---------------------------------

            text = re.sub(

                r"^(create|build|generate|make)\s+",

                "",

                text,

                flags=re.IGNORECASE,

            )

            # ---------------------------------
            # Remove filler words
            # ---------------------------------

            text = re.sub(

                r"\b(an|a|the|project|application|app)\b",

                "",

                text,

                flags=re.IGNORECASE,

            )

            text = re.sub(

                r"\s+",

                " ",

                text,

            ).strip()

            text = re.sub(

                r"[^A-Za-z0-9 ]",

                "",

                text,

            )

            words = text.split()

            if not words:

                base_name = self.DEFAULT_NAME

            else:

                parts = []

                for word in words:

                    key = word.lower()

                    if key in self.SPECIAL_WORDS:

                        parts.append(

                            self.SPECIAL_WORDS[key]

                        )

                    else:

                        parts.append(

                            word.capitalize()

                        )

                base_name = "".join(parts)

        # -------------------------------
        # Unique Folder Name
        # -------------------------------

        candidate = base_name

        counter = 1

        while (output_directory / candidate).exists():

            candidate = f"{base_name}_{counter}"

            counter += 1

        return candidate