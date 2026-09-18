# ===========================
# JARVIS PRO SETTINGS
# ===========================

from config.environment import get_env

APP_NAME = "JARVIS"

VERSION = "1.0"

AUTHOR = "Madan"

VOICE = "male"

LANGUAGE = "en"

DEBUG = True

WAKE_WORDS = [
    "jarvis",
    "hey jarvis",
    "hello jarvis"
]

# ===========================
# AI
# ===========================

AI_PROVIDER = "ollama"

OLLAMA_MODEL = "qwen2.5:3b"

OLLAMA_URL = get_env(
    "OLLAMA_API_URL",
    "http://localhost:11434/api/generate",
)

# ===========================
# Local Vision / Face Recognition
# ===========================

def _float_setting(name, default):
    try:
        return float(get_env(name, str(default)))
    except (TypeError, ValueError):
        return float(default)


def _int_setting(name, default):
    try:
        return int(get_env(name, str(default)))
    except (TypeError, ValueError):
        return int(default)


VISION_FACE_RECOGNITION_THRESHOLD = _float_setting(
    "JARVIS_VISION_FACE_RECOGNITION_THRESHOLD", 75.0
)
VISION_FACE_MIN_SIZE = _int_setting("JARVIS_VISION_FACE_MIN_SIZE", 80)
VISION_FACE_MIN_QUALITY = _float_setting("JARVIS_VISION_FACE_MIN_QUALITY", 0.20)
VISION_REGISTRATION_SAMPLE_COUNT = _int_setting(
    "JARVIS_VISION_REGISTRATION_SAMPLE_COUNT", 5
)
VISION_REGISTRATION_MAX_ATTEMPTS = _int_setting(
    "JARVIS_VISION_REGISTRATION_MAX_ATTEMPTS", 30
)
VISION_REGISTRATION_SAMPLE_INTERVAL = _float_setting(
    "JARVIS_VISION_REGISTRATION_SAMPLE_INTERVAL", 0.25
)
VISION_SPEECH_COOLDOWN = _float_setting("JARVIS_VISION_SPEECH_COOLDOWN", 5.0)
