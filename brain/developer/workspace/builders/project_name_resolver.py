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
    Generates a clean, concise, unique project name.

    The resolver intentionally uses deterministic local rules so
    project folder names do not depend on AI-generated verbose names.
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
        "python": "Python",
        "cpp": "CPP",
        "c++": "CPP",
    }

    # Words that describe the command rather than the project itself.
    COMMAND_WORDS = {
        "create",
        "build",
        "generate",
        "make",
        "develop",
        "design",
        "write",
        "developing",
        "creating",
        "building",
    }

    # Generic words that should not normally appear in a folder name.
    GENERIC_WORDS = {
        "a",
        "an",
        "the",
        "project",
        "application",
        "app",
        "program",
        "software",
        "system",
        "solution",
        "tool",
        "website",
        "web",
        "site",
        "script",
    }

    # Implementation/detail words that commonly make names unnecessarily long.
    DETAIL_WORDS = {
        "using",
        "use",
        "with",
        "without",
        "including",
        "include",
        "based",
        "built",
        "support",
        "supports",
        "feature",
        "features",
        "for",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "from",
        "that",
        "which",
        "this",
        "these",
        "those",
        "modern",
        "responsive",
        "simple",
        "basic",
        "advanced",
    }

    # Detailed implementation phrases that should not become folder names.
    DETAIL_PHRASES = (
        r"\busing\s+html\b",
        r"\busing\s+css\b",
        r"\busing\s+javascript\b",
        r"\bhtml\s+css\s+javascript\b",
        r"\bhtml\s+css\s+js\b",
        r"\bwith\s+dark\s+mode\b",
        r"\bwith\s+light\s+mode\b",
        r"\bwith\s+responsive\s+design\b",
        r"\bwith\s+modern\s+ui\b",
        r"\bwith\s+modern\s+responsive\s+ui\b",
        r"\baddition\s*,?\s*subtraction\s*,?\s*multiplication\s*(?:and\s*)?division\b",
        r"\baddition\s+subtraction\s+multiplication\s+division\b",
    )

    # Common operation/detail words that are useful in the request but
    # unnecessary in a concise project folder name.
    OPERATION_WORDS = {
        "addition",
        "subtraction",
        "multiplication",
        "division",
        "calculator",
        "calculation",
    }

    # Keep important project nouns while limiting excessive description.
    PROJECT_NOUNS = {
        "calculator",
        "portfolio",
        "dashboard",
        "parking",
        "attendance",
        "chatbot",
        "assistant",
        "automation",
        "robot",
        "robotics",
        "weather",
        "music",
        "player",
        "inventory",
        "billing",
        "login",
        "authentication",
        "booking",
        "ecommerce",
        "shop",
        "store",
        "blog",
        "camera",
        "vision",
        "monitor",
        "tracker",
        "manager",
        "management",
        "system",
        "website",
        "app",
    }

    def resolve(
        self,
        project: GeneratedProject,
        output_directory: Path,
    ) -> str:
        """
        Resolve a clean and unique project folder name.
        """

        # -------------------------------------------------
        # Arduino / ESP sketches
        # -------------------------------------------------
        #
        # Arduino requires the folder name and .ino filename
        # to match. Preserve the actual .ino filename exactly.
        #
        ino_name = self._get_ino_name(project)

        if ino_name:
            base_name = ino_name

        else:
            # -------------------------------------------------
            # Always derive normal project names from the
            # original user request instead of trusting a
            # potentially verbose AI-generated project.name.
            # -------------------------------------------------

            text = (project.user_request or "").strip()

            if not text:
                text = (project.name or "").strip()

            base_name = self._build_clean_name(
                text,
                project,
            )

        if not base_name:
            base_name = self.DEFAULT_NAME

        # -------------------------------------------------
        # Unique Folder Name
        # -------------------------------------------------

        candidate = base_name
        counter = 1

        while (output_directory / candidate).exists():
            candidate = f"{base_name}_{counter}"
            counter += 1

        return candidate

    # -----------------------------------------------------
    # Arduino Helper
    # -----------------------------------------------------

    @staticmethod
    def _get_ino_name(project: GeneratedProject) -> str:
        """
        Return the first .ino filename stem.

        This preserves Arduino's required sketch/folder
        naming relationship.
        """

        for generated_file in project.files:
            path = str(generated_file.path).replace("\\", "/")

            if path.lower().endswith(".ino"):
                return Path(path).stem

        return ""

    # -----------------------------------------------------
    # Clean Project Name
    # -----------------------------------------------------

    def _build_clean_name(
        self,
        text: str,
        project: GeneratedProject,
    ) -> str:
        """
        Convert a natural-language request into a concise
        PascalCase project name.
        """

        # Remove implementation/detail phrases first.
        for pattern in self.DETAIL_PHRASES:
            text = re.sub(
                pattern,
                " ",
                text,
                flags=re.IGNORECASE,
            )

        # Normalize punctuation.
        text = re.sub(
            r"[^A-Za-z0-9+# ]",
            " ",
            text,
        )

        # Tokenize.
        words = text.split()

        cleaned = []

        for word in words:
            key = word.lower()

            # Command words.
            if key in self.COMMAND_WORDS:
                continue

            # Generic words.
            if key in self.GENERIC_WORDS:
                continue

            # Detail/filler words.
            if key in self.DETAIL_WORDS:
                continue

            cleaned.append(word)

        # -------------------------------------------------
        # Prefer important project words.
        # -------------------------------------------------

        important = []
        technology = []

        for word in cleaned:
            key = word.lower()

            if key in self.SPECIAL_WORDS:
                technology.append(word)
                continue

            if key in self.PROJECT_NOUNS:
                important.append(word)

        # -------------------------------------------------
        # Language prefix
        # -------------------------------------------------

        language = str(getattr(project, "language", "") or "").lower()

        language_name = ""

        if "python" in language:
            language_name = "Python"
        elif "javascript" in language or language == "js":
            language_name = "JavaScript"
        elif "typescript" in language or language == "ts":
            language_name = "TypeScript"
        elif "cpp" in language or "c++" in language:
            language_name = "CPP"
        elif language == "c":
            language_name = "C"

        # -------------------------------------------------
        # Build concise name
        # -------------------------------------------------

        result_words = []

        if language_name:
            result_words.append(language_name)

        # Add important project nouns in request order.
        for word in important:
            if word.lower() not in {
                item.lower() for item in result_words
            }:
                result_words.append(word)

        # If no strong project noun was found, keep a small
        # amount of meaningful request content.
        if len(result_words) <= 1:
            fallback = []

            for word in cleaned:
                key = word.lower()

                if key in self.SPECIAL_WORDS:
                    continue

                if len(key) <= 2:
                    continue

                fallback.append(word)

            # Keep only the first few meaningful words.
            result_words.extend(fallback[:3])

        # -------------------------------------------------
        # Special technology-only projects
        # -------------------------------------------------

        if not result_words and technology:
            result_words.extend(technology[:2])

        # -------------------------------------------------
        # Final formatting
        # -------------------------------------------------

        parts = []

        for word in result_words:
            key = word.lower()

            if key in self.SPECIAL_WORDS:
                parts.append(self.SPECIAL_WORDS[key])
            else:
                # Preserve existing acronym-like words.
                if word.isupper() and len(word) <= 5:
                    parts.append(word)
                else:
                    parts.append(word.capitalize())

        name = "".join(parts)

        # Final safety cleanup.
        name = re.sub(
            r"[^A-Za-z0-9_]+",
            "",
            name,
        )

        return name or self.DEFAULT_NAME