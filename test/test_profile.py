from brain.profile_manager import ProfileManager

profile = ProfileManager()

profile.set("name", "Madan")

profile.set("current_project", "JARVIS PRO")

profile.set("github", "madanr")

print()

print(profile)

print()

print(profile.as_dict())

print()

print(profile.get("current_project"))