"""
JARVIS PRO
One-Shot Vision Skill

Vision automatically starts when a vision command is requested.

Flow:

    Vision command
        ↓
    Start Vision
        ↓
    Wait for scene
        ↓
    Perform requested operation
        ↓
    Stop Vision
        ↓
    Camera released

Vision is NOT persistent.

Camera skill itself is not modified.
"""

from core.registry import register

from skills.camera.vision_loop import vision_loop
from skills.camera.vision_query import vision_query


# =========================================================
# Vision Session Helpers
# =========================================================

def _start_vision():
    """
    Start Vision for the current request.
    """

    if vision_loop.running:

        print(
            "[VISION] Already running."
        )

        return True

    print(
        "[VISION] Starting one-shot vision..."
    )

    return vision_loop.start()


def _stop_vision():
    """
    Stop Vision after the current request.
    """

    if not vision_loop.running:

        return True

    print(
        "[VISION] Stopping one-shot vision..."
    )

    return vision_loop.stop()


# =========================================================
# Vision Start
#
# Compatibility command.
#
# We keep this registered, but normal vision requests
# no longer need it.
# =========================================================

def vision_start(data=None):

    return _start_vision()


# =========================================================
# Vision Stop
#
# Manual emergency/compatibility command.
# =========================================================

def vision_stop(data=None):

    return _stop_vision()


# =========================================================
# Describe Scene
# =========================================================

def vision_describe(data=None):

    started = False

    try:

        # ---------------------------------------------
        # Start Vision
        # ---------------------------------------------

        if not vision_loop.running:

            if not _start_vision():

                return {
                    "error": "Unable to start vision."
                }

            started = True

        # ---------------------------------------------
        # Query scene
        # ---------------------------------------------

        print(
            "[VISION] Describing scene..."
        )

        return vision_query.describe()

    except Exception as e:

        print(
            "[VISION ERROR] Describe:",
            e
        )

        return {
            "error": str(e)
        }

    finally:

        # ---------------------------------------------
        # Always shut Vision down after this request.
        # ---------------------------------------------

        if started:

            _stop_vision()


# =========================================================
# Count Object
# =========================================================

def vision_count(data=None):

    started = False

    try:

        # ---------------------------------------------
        # Start Vision
        # ---------------------------------------------

        if not vision_loop.running:

            if not _start_vision():

                return {
                    "error": "Unable to start vision."
                }

            started = True

        # ---------------------------------------------
        # Validate input
        # ---------------------------------------------

        if not isinstance(data, dict):

            data = {}

        object_name = data.get("object")

        if not object_name:

            return {
                "error": "Object name is required."
            }

        # ---------------------------------------------
        # Count
        # ---------------------------------------------

        print(
            f"[VISION] Counting: {object_name}"
        )

        return vision_query.count(
            object_name
        )

    except Exception as e:

        print(
            "[VISION ERROR] Count:",
            e
        )

        return {
            "error": str(e)
        }

    finally:

        if started:

            _stop_vision()


# =========================================================
# Check Object
# =========================================================

def vision_check(data=None):

    started = False

    try:

        # ---------------------------------------------
        # Start Vision
        # ---------------------------------------------

        if not vision_loop.running:

            if not _start_vision():

                return {
                    "error": "Unable to start vision."
                }

            started = True

        # ---------------------------------------------
        # Validate input
        # ---------------------------------------------

        if not isinstance(data, dict):

            data = {}

        object_name = data.get("object")

        if not object_name:

            return {
                "error": "Object name is required."
            }

        # ---------------------------------------------
        # Check object
        # ---------------------------------------------

        print(
            f"[VISION] Checking: {object_name}"
        )

        return vision_query.has_object(
            object_name
        )

    except Exception as e:

        print(
            "[VISION ERROR] Check:",
            e
        )

        return {
            "error": str(e)
        }

    finally:

        if started:

            _stop_vision()


# =========================================================
# Objects At Position
# =========================================================

def vision_position(data=None):

    started = False

    try:

        # ---------------------------------------------
        # Start Vision
        # ---------------------------------------------

        if not vision_loop.running:

            if not _start_vision():

                return {
                    "error": "Unable to start vision."
                }

            started = True

        # ---------------------------------------------
        # Validate input
        # ---------------------------------------------

        if not isinstance(data, dict):

            data = {}

        position = data.get("position")

        if not position:

            return {
                "error": "Position is required."
            }

        # ---------------------------------------------
        # Query position
        # ---------------------------------------------

        print(
            f"[VISION] Checking position: {position}"
        )

        return vision_query.objects_at(
            position
        )

    except Exception as e:

        print(
            "[VISION ERROR] Position:",
            e
        )

        return {
            "error": str(e)
        }

    finally:

        if started:

            _stop_vision()


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


print(
    "[VISION SKILL] Registered."
)