"""
JARVIS PRO
Personal Links Configuration

Stores user-specific websites, profiles,
repositories, dashboards and project links.

This file contains configuration only.
No routing or browser logic belongs here.
"""

# =========================================================
# Personal Links
# =========================================================

PERSONAL_LINKS = {

    # -----------------------------------------------------
    # Social / Profiles
    # -----------------------------------------------------

    "github": "https://github.com/Madannayak003",
    "github_profile": "https://github.com/Madannayak003",
    
    "github_repository": "https://github.com/Madannayak003?tab=repositories",

    "facebook": "",
    "facebook_profile": "",

    "linkedin": "",
    "linkedin_profile": "",

    # -----------------------------------------------------
    # Personal Websites
    # -----------------------------------------------------

    "website": "https://madanr.netlify.app/",
    "portfolio": "https://madanr.netlify.app/",

    "iot": "",
    "iot_website": "",
    
    "iotrix_lab": "https://iotrix-lab.vercel.app/",

    # -----------------------------------------------------
    # JARVIS
    # -----------------------------------------------------

    "jarvis_github": "https://github.com/Madannayak003/JARVIS-PRO",
    "jarvis_repository": "https://github.com/Madannayak003/JARVIS-PRO",

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------

    "smart_parking": "",
    "atmers": "",
}


# =========================================================
# Get Link
# =========================================================

def get_link(name):
    """
    Return a configured personal link.

    Returns:
        str | None
    """

    if not name:
        return None

    key = str(name).strip().lower()

    return PERSONAL_LINKS.get(key)


# =========================================================
# Check Link
# =========================================================

def has_link(name):
    """
    Return True when a personal link is configured.
    """

    link = get_link(name)

    return bool(link)