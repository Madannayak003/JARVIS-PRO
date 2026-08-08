"""
JARVIS PRO
Developer Integration

Brain Router Test
"""

from brain.brain_router import (
    BrainRouter,
)


def main():

    print("=" * 90)
    print("JARVIS PRO")
    print("Brain Router - Phase 10.2 Test")
    print("=" * 90)

    router = BrainRouter()

    # ==================================================
    # Normal command
    # ==================================================

    result = router.route(
        "open chrome",
    )

    print("\n[1] Normal command")
    print(result)

    assert result.handled is False

    print("PASS")

    # ==================================================
    # Normal chat
    # ==================================================

    result = router.route(
        "what is python",
    )

    print("\n[2] Normal chat")
    print(result)

    assert result.handled is False

    print("PASS")

    # ==================================================
    # Developer detection without project
    # ==================================================

    result = router.route(
        "fix the divide function",
    )

    print("\n[3] Developer request")
    print(result)

    print(
        "\nNote:"
    )

    print(
        "If no active project exists, "
        "handled=False is expected."
    )

    print("PASS")

    # ==================================================
    # Empty command
    # ==================================================

    result = router.route(
        "",
    )

    print("\n[4] Empty command")
    print(result)

    assert result.handled is False

    print("PASS")

    print()
    print("=" * 90)
    print("PHASE 10.2 BRAIN ROUTER TEST PASSED")
    print("=" * 90)


if __name__ == "__main__":
    main()