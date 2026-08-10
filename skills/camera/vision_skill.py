"""
JARVIS PRO
Vision Skill

Connects the Vision Engine / Vision Query system
to the central JARVIS skill registry.
"""

from core.registry import register

from skills.camera.vision_loop import vision_loop
from skills.camera.vision_query import vision_query


# =========================================================
# Vision Start
# =========================================================

def vision_start(data=None):

    return vision_loop.start()


# =========================================================
# Vision Stop
# =========================================================

def vision_stop(data=None):

    return vision_loop.stop()


# =========================================================
# Describe Scene
# =========================================================

def vision_describe(data=None):

    if not vision_loop.running:
        vision_loop.start()

    return vision_query.describe()


# =========================================================
# Count Object
# =========================================================

def vision_count(data=None):

    if not vision_loop.running:
        vision_loop.start()

    if not isinstance(data, dict):
        data = {}

    object_name = data.get("object")

    if not object_name:
        return {
            "error": "Object name is required."
        }

    return vision_query.count(
        object_name
    )


# =========================================================
# Check Object
# =========================================================

def vision_check(data=None):

    if not vision_loop.running:
        vision_loop.start()

    if not isinstance(data, dict):
        data = {}

    object_name = data.get("object")

    if not object_name:
        return {
            "error": "Object name is required."
        }

    return vision_query.has_object(
        object_name
    )


# =========================================================
# Objects At Position
# =========================================================

def vision_position(data=None):

    if not vision_loop.running:
        vision_loop.start()

    if not isinstance(data, dict):
        data = {}

    position = data.get("position")

    if not position:
        return {
            "error": "Position is required."
        }

    return vision_query.objects_at(
        position
    )


# =========================================================
# Registry
# =========================================================

register(
    "vision_start",
    vision_start,
    category="camera",
)

register(
    "vision_stop",
    vision_stop,
    category="camera",
)

register(
    "vision_describe",
    vision_describe,
    category="camera",
)

register(
    "vision_count",
    vision_count,
    category="camera",
)

register(
    "vision_check",
    vision_check,
    category="camera",
)

register(
    "vision_position",
    vision_position,
    category="camera",
)


print("[VISION SKILL] Registered.")