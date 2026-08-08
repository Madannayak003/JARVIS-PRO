"""
JARVIS PRO
Skill Category Migration

Physically organizes skills/ into category folders while
preserving existing skill actions and updating imports.
"""

from pathlib import Path
import shutil
import re


ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / "skills"


# ============================================================
# Physical Skill Organization
# ============================================================

CATEGORIES = {

    "ai": [
        "clarify.py",
    ],

    "assistant": [
        "greetings.py",
    ],

    "browser": [
        "browser_ai.py",
        "browser_automation.py",
        "browser_controller.py",
        "browser_open.py",
        "browser_state.py",
        "chrome.py",
        "navigation.py",
        "youtube.py",
    ],

    "browser_control": [
        "browser_controls.py",
    ],

    "camera": [
        "camera.py",
        "vision.py",
    ],

    "communication": [
        "chatgpt.py",
        "contact.py",
        "email.py",
        "github.py",
        "telegram.py",
        "whatsapp.py",
    ],

    "files": [
        "fileinfo.py",
        "files.py",
        "recent.py",
        "recycle.py",
        "zip_manager.py",
    ],

    "media": [
        "media.py",
        "spotify.py",
    ],

    "memory": [
        "memory.py",
        "notes.py",
        "reminders.py",
    ],

    "network": [
        "bluetooth.py",
        "wifi.py",
        "weather.py",
    ],

    "screen": [
        "clipboard.py",
        "screenshot.py",
        "screenshot_ai.py",
    ],

    "system": [
        "battery.py",
        "brightness.py",
        "process.py",
        "system.py",
        "taskmanager.py",
        "volume.py",
    ],

    "utilities": [
        "calculator.py",
        "search.py",
        "time_skill.py",
    ],
}


# ============================================================
# Build file -> category map
# ============================================================

FILE_CATEGORY = {}

for category, files in CATEGORIES.items():

    for filename in files:

        if filename in FILE_CATEGORY:

            raise RuntimeError(
                f"Duplicate skill assignment: {filename}"
            )

        FILE_CATEGORY[filename] = category


# ============================================================
# Validation
# ============================================================

def validate():

    if not SKILLS.exists():

        raise RuntimeError(
            f"Skills directory not found: {SKILLS}"
        )

    existing = {
        p.name
        for p in SKILLS.glob("*.py")
        if p.name not in {
            "__init__.py",
            "loader.py",
        }
    }

    configured = set(FILE_CATEGORY)

    missing_from_config = existing - configured
    missing_from_disk = configured - existing

    if missing_from_config:

        raise RuntimeError(
            "These skill files are not categorized:\n"
            + "\n".join(
                sorted(missing_from_config)
            )
        )

    if missing_from_disk:

        raise RuntimeError(
            "These configured files do not exist:\n"
            + "\n".join(
                sorted(missing_from_disk)
            )
        )


# ============================================================
# Create package folders
# ============================================================

def create_packages():

    for category in CATEGORIES:

        folder = SKILLS / category

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        init_file = folder / "__init__.py"

        if not init_file.exists():

            init_file.write_text(
                "",
                encoding="utf-8",
            )


# ============================================================
# Move skill files
# ============================================================

def move_skills():

    moved = []

    for category, files in CATEGORIES.items():

        destination = SKILLS / category

        for filename in files:

            source = SKILLS / filename
            target = destination / filename

            if target.exists():

                print(
                    f"[SKILL MIGRATION] Already exists: "
                    f"{category}/{filename}"
                )

                continue

            if source.exists():

                shutil.move(
                    str(source),
                    str(target),
                )

                moved.append(
                    (filename, category)
                )

                print(
                    f"[SKILL MIGRATION] "
                    f"{filename} -> {category}/"
                )

    return moved


# ============================================================
# Update Python imports
# ============================================================

def update_imports():

    python_files = []

    # Active project files only.
    # Archive is intentionally NOT modified.

    for folder in [
        ROOT / "core",
        ROOT / "skills",
        ROOT / "main.py",
    ]:

        if folder.is_file():

            python_files.append(folder)

        elif folder.exists():

            python_files.extend(
                folder.rglob("*.py")
            )

    # Include brain / ai / services if they exist.
    for folder_name in [
        "brain",
        "ai",
        "services",
    ]:

        folder = ROOT / folder_name

        if folder.exists():

            python_files.extend(
                folder.rglob("*.py")
            )

    # Build import replacements.
    replacements = {}

    for filename, category in FILE_CATEGORY.items():

        module = filename[:-3]

        old = f"skills.{module}"
        new = f"skills.{category}.{module}"

        replacements[old] = new

    changed = []

    for path in python_files:

        if not path.exists():
            continue

        # Do not modify this migration script.
        if path.name == "skill_categories.py":
            continue

        try:

            text = path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            continue

        original = text

        for old, new in replacements.items():

            text = text.replace(
                old,
                new,
            )

        if text != original:

            path.write_text(
                text,
                encoding="utf-8",
            )

            changed.append(path)

            print(
                f"[IMPORT UPDATE] {path.relative_to(ROOT)}"
            )

    return changed


# ============================================================
# Update skills.loader
# ============================================================

def update_loader():

    loader = SKILLS / "loader.py"

    if not loader.exists():

        raise RuntimeError(
            "skills/loader.py not found."
        )

    text = loader.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Preserve the CURRENT active loader list.
    #
    # We only change:
    #
    #     skills.module
    #
    # into:
    #
    #     skills.category.module
    #
    # We DO NOT activate dormant skills.
    # --------------------------------------------------------

    pattern = re.compile(
        r'SKILLS\s*=\s*\[(.*?)\]',
        re.DOTALL,
    )

    match = pattern.search(text)

    if not match:

        raise RuntimeError(
            "Could not locate SKILLS list "
            "inside skills/loader.py"
        )

    current_block = match.group(1)

    current_modules = re.findall(
        r'"([^"]+)"',
        current_block,
    )

    if not current_modules:

        raise RuntimeError(
            "Current SKILLS list is empty."
        )

    new_modules = []

    for module in current_modules:

        filename = module + ".py"

        category = FILE_CATEGORY.get(filename)

        if category is None:

            raise RuntimeError(
                f"Active skill '{module}' "
                f"has no category."
            )

        new_modules.append(
            f"{category}.{module}"
        )

    new_list = "SKILLS = [\n"

    for module in new_modules:

        new_list += (
            f'    "{module}",\n'
        )

    new_list += "]"

    text = pattern.sub(
        new_list,
        text,
        count=1,
    )

    loader.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "[LOADER UPDATE] "
        "Current active skills preserved."
    )

    print(
        f"[LOADER UPDATE] "
        f"Active modules preserved: {len(new_modules)}"
    )


# ============================================================
# Summary
# ============================================================

def print_summary():

    print()
    print("=" * 70)
    print("JARVIS PRO SKILL CATEGORY MIGRATION")
    print("=" * 70)

    total = sum(
        len(files)
        for files in CATEGORIES.values()
    )

    print(
        f"Categories : {len(CATEGORIES)}"
    )

    print(
        f"Skill files : {total}"
    )

    print()

    for category, files in CATEGORIES.items():

        print(
            f"{category:18} : {len(files)}"
        )

    print()
    print(
        "Migration completed successfully."
    )
    print(
        "Existing skill actions were not changed."
    )
    print("=" * 70)


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 70)
    print("JARVIS PRO - SKILL CATEGORY MIGRATION")
    print("=" * 70)
    print()

    print("[1/5] Validating skill files...")
    validate()
    print("      Validation OK")

    print()
    print("[2/5] Creating category packages...")
    create_packages()
    print("      Packages OK")

    print()
    print("[3/5] Moving skill files...")
    move_skills()
    print("      Files organized")

    print()
    print("[4/5] Updating imports...")
    update_imports()
    print("      Imports updated")

    print()
    print("[5/5] Updating loader...")
    update_loader()
    print("      Loader updated")

    print_summary()


if __name__ == "__main__":
    main()