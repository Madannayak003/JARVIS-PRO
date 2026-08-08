"""
JARVIS PRO
Core Skill Registry

Registry V2

Responsibilities:
- Register skill actions
- Execute registered actions
- Validate registrations
- Prevent accidental invalid registrations
- Provide registry inspection helpers
- Preserve compatibility with existing skills
"""

from core.fallback import fallback


# =========================================================
# Skill Registry
# =========================================================

SKILLS = {}


# =========================================================
# Register
# =========================================================

def register(action, handler):
    """
    Register a skill action.

    Existing skills use:

        register("action_name", handler)

    This API remains backward compatible.
    """

    if not isinstance(action, str):
        raise TypeError(
            "Skill action must be a string."
        )

    action = action.strip()

    if not action:
        raise ValueError(
            "Skill action cannot be empty."
        )

    if not callable(handler):
        raise TypeError(
            f"Handler for '{action}' must be callable."
        )

    # -----------------------------------------
    # Duplicate registration
    # -----------------------------------------

    existing = SKILLS.get(action)

    if existing is not None and existing is not handler:

        print(
            f"[REGISTRY WARNING] "
            f"Replacing existing handler for '{action}'"
        )

    SKILLS[action] = handler


# =========================================================
# Unregister
# =========================================================

def unregister(action):
    """
    Remove a registered action.

    Returns:
        True  -> removed
        False -> action was not registered
    """

    if not isinstance(action, str):
        return False

    action = action.strip()

    if action in SKILLS:

        del SKILLS[action]

        return True

    return False


# =========================================================
# Get Handler
# =========================================================

def get_handler(action):
    """
    Return the handler registered for an action.

    Returns:
        handler or None
    """

    if not isinstance(action, str):
        return None

    return SKILLS.get(action.strip())


# =========================================================
# Has Skill
# =========================================================

def has_skill(action):
    """
    Check whether an action is registered.
    """

    if not isinstance(action, str):
        return False

    return action.strip() in SKILLS


# =========================================================
# Execute
# =========================================================

def execute(action, data=None):
    """
    Execute a registered skill action.

    Falls back to the AI fallback system when
    the action is unknown.
    """

    if not isinstance(action, str):

        print(
            f"[REGISTRY ERROR] Invalid action: {action!r}"
        )

        return False

    action = action.strip()

    print(
        "Requested action :",
        repr(action)
    )

    print(
        "Available actions:",
        sorted(SKILLS.keys())
    )

    handler = get_handler(action)

    # -----------------------------------------
    # Registered skill
    # -----------------------------------------

    if handler:

        try:

            return handler(data)

        except Exception as e:

            print(
                f"[REGISTRY ERROR] "
                f"Action '{action}' failed:"
            )

            print(e)

            return False

    # -----------------------------------------
    # Unknown action
    # -----------------------------------------

    print(
        f"\nUnknown action : {action}"
    )

    print(
        "\nTrying AI fallback...\n"
    )

    try:

        result = fallback(action)

        print(result)

        return result

    except Exception as e:

        print(
            f"[REGISTRY FALLBACK ERROR] {e}"
        )

        return False


# =========================================================
# List Skills
# =========================================================

def list_skills():
    """
    Return all registered skill actions.
    """

    return list(SKILLS.keys())


# =========================================================
# Registry Information
# =========================================================

def skill_count():
    """
    Return the number of registered actions.
    """

    return len(SKILLS)


def registry_info():
    """
    Return basic registry diagnostics.
    """

    return {
        "count": len(SKILLS),
        "actions": sorted(SKILLS.keys()),
    }