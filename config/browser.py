from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROME_PROFILE = PROJECT_ROOT / "data" / "chrome_profile"

WHATSAPP_WEB = "https://web.whatsapp.com"

HEADLESS = False

WAIT_TIMEOUT = 20