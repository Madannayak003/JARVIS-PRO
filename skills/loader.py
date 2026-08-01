from importlib import import_module

SKILLS = [
    "memory",
    "clarify",
    "media",
    "volume",
    "browser_ai",
    "system",
    "brightness",
    "screenshot",
    "clipboard",
    "battery",
    "wifi",
    "bluetooth",
    "process",
    "taskmanager",
    "screenshot_ai",
    "files",
    "search",
    "zip_manager",
    "camera",
    "time_skill",
    "github",
    "chatgpt",
    "spotify",
    "greetings",
    "whatsapp",
    "contact",
]

def load_all():
    for skill in SKILLS:
        import_module(f"skills.{skill}")