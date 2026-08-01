# ===========================
# JARVIS PRO SETTINGS
# ===========================

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

OLLAMA_URL = "http://localhost:11434/api/generate"