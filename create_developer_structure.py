from pathlib import Path

# -------------------------------------------------------
# JARVIS PRO - Developer V2 Structure Creator
# -------------------------------------------------------

BRAIN_DIR = Path("brain")
DEVELOPER_DIR = BRAIN_DIR / "developer"

FOLDERS = [
    "api",
    "models",
    "analyzer",
    "planner",
    "prompts",
    "generator",
    "validator",
    "workspace",
    "editor",
    "memory",
    "integration",
    "utils",
    "tests",
]

# -------------------------------------------------------
# Create developer folder
# -------------------------------------------------------

DEVELOPER_DIR.mkdir(parents=True, exist_ok=True)

# developer package
(DEVELOPER_DIR / "__init__.py").touch(exist_ok=True)

# developer entry point
(DEVELOPER_DIR / "developer.py").touch(exist_ok=True)

# -------------------------------------------------------
# Create subfolders
# -------------------------------------------------------

for folder in FOLDERS:

    folder_path = DEVELOPER_DIR / folder

    folder_path.mkdir(parents=True, exist_ok=True)

    # make every folder a package
    (folder_path / "__init__.py").touch(exist_ok=True)

print("=" * 50)
print("Developer V2 folder structure created successfully.")
print("=" * 50)

print("\nCreated:\n")

print("brain/")
print("└── developer/")

for folder in FOLDERS:
    print(f"    ├── {folder}/")

print("    └── developer.py")