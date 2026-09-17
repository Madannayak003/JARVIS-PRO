"""
JARVIS PRO
Personal Links Configuration

Stores user-specific websites, profiles,
repositories, dashboards and project links.

This file contains configuration only.
No routing or browser logic belongs here.
"""

from config.environment import get_env

# =========================================================
# Personal Links
# =========================================================

PERSONAL_LINKS = {

    # -----------------------------------------------------
    # Social / Profiles
    # -----------------------------------------------------

    "github": get_env("PERSONAL_GITHUB_URL"),
    "github_profile": get_env("PERSONAL_GITHUB_PROFILE_URL"),
    
    "github_repository": get_env("PERSONAL_GITHUB_REPOSITORIES_URL"),

    "facebook": get_env("PERSONAL_FACEBOOK_URL"),
    "facebook_profile": get_env("PERSONAL_FACEBOOK_PROFILE_URL"),

    "linkedin": get_env("PERSONAL_LINKEDIN_URL"),
    "linkedin_profile": get_env("PERSONAL_LINKEDIN_PROFILE_URL"),

    # -----------------------------------------------------
    # Personal Websites
    # -----------------------------------------------------

    "website": get_env("PERSONAL_WEBSITE_URL"),
    "portfolio": get_env("PERSONAL_PORTFOLIO_URL"),

    "iot": get_env("PERSONAL_IOT_URL"),
    "iot_website": get_env("PERSONAL_IOT_WEBSITE_URL"),
    
    "iotrix_lab": get_env("IOTRIX_LAB_URL"),

    # -----------------------------------------------------
    # JARVIS
    # -----------------------------------------------------

    "jarvis_github": get_env("JARVIS_GITHUB_URL"),
    "jarvis_repository": get_env("JARVIS_REPOSITORY_URL"),

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------

    "smart_parking": get_env("SMART_PARKING_URL"),
    "atmers": get_env("ATMERS_URL"),
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
