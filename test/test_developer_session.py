from pathlib import Path

from brain.developer.developer_session import DeveloperSessionManager

# ==========================================================
# Create Session Manager
# ==========================================================

session = DeveloperSessionManager()

# ==========================================================
# Initial State
# ==========================================================

print("=" * 60)
print("INITIAL")
print("=" * 60)

print(session.get())

print()

# ==========================================================
# Update Session
# ==========================================================

session.update(

    project_name="Calculator",

    project_path=Path("workspace/Python/Calculator"),

    language="python",

    action="edit",

    last_request="update calculator",

    editing_existing=True

)

print("=" * 60)
print("UPDATED")
print("=" * 60)

print(session.get())

print()

print("Has Project :", session.has_project())
print("Project     :", session.project_name())
print("Path        :", session.project_path())

print()

# ==========================================================
# Clear Session
# ==========================================================

session.clear()

print("=" * 60)
print("CLEARED")
print("=" * 60)

print(session.get())