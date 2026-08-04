"""
JARVIS PRO
Developer Editor

Editor Rules
"""

# --------------------------------------------------
# Supported edit actions
# --------------------------------------------------

SUPPORTED_ACTIONS = {

    "ADD",
    "REMOVE",
    "UPDATE",
    "MODIFY",
    "FIX",
    "REPLACE",
    "RENAME",
    "REFACTOR",
    "OPTIMIZE",
    "FORMAT",

}

# --------------------------------------------------
# Prompt limits
# --------------------------------------------------

MAX_PROMPT_CHARACTERS = 50000

MAX_FILES_PER_REQUEST = 10

# --------------------------------------------------
# Safety
# --------------------------------------------------

CREATE_BACKUP = True

VALIDATE_PATCHES = True

ALLOW_NEW_FILES = True

ALLOW_DELETE_FILES = False

ALLOW_OVERWRITE = True

# --------------------------------------------------
# File extensions
# --------------------------------------------------

SUPPORTED_EXTENSIONS = {

    ".py",
    ".ino",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".md",

}