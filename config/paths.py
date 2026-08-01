from pathlib import Path

# Project Root
ROOT = Path(__file__).resolve().parent.parent

# Data Root
DATA = ROOT / "data"

# Standard Data Folders
CACHE = DATA / "cache"
CAPTURES = DATA / "captures"
DOCUMENTS = DATA / "documents"
DOWNLOADS = DATA / "downloads"
EXPORTS = DATA / "exports"
FACES = DATA / "faces"
LOGS = DATA / "logs"
MEMORIES = DATA / "memories"
RECORDINGS = DATA / "recordings"
SCREENSHOTS = DATA / "screenshots"
TEMP = DATA / "temp"

# Create folders automatically
for folder in [
    DATA,
    CACHE,
    CAPTURES,
    DOCUMENTS,
    DOWNLOADS,
    EXPORTS,
    FACES,
    LOGS,
    MEMORIES,
    RECORDINGS,
    SCREENSHOTS,
    TEMP,
]:
    folder.mkdir(parents=True, exist_ok=True)