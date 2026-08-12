from voice.mode import get_mode

from hud.integration import HUDIntegration
from hud.manager import hud


print()
print("=== REAL HUD MODE TEST ===")
print()

# -------------------------------------------------
# Real voice mode
# -------------------------------------------------

mode = get_mode()

print(
    "[TEST] Real voice mode:",
    mode
)

# -------------------------------------------------
# Integration status
# -------------------------------------------------

print(
    "[TEST] HUD integration enabled:",
    HUDIntegration.enabled()
)

# -------------------------------------------------
# Before
# -------------------------------------------------

print(
    "[TEST] HUD mode BEFORE:",
    hud.state.voice_mode
)

# -------------------------------------------------
# Send real mode
# -------------------------------------------------

HUDIntegration.voice_mode(
    mode
)

# -------------------------------------------------
# After
# -------------------------------------------------

print(
    "[TEST] HUD mode AFTER:",
    hud.state.voice_mode
)

# -------------------------------------------------
# Direct adapter verification
# -------------------------------------------------

from hud.adapter import HUDAdapter

HUDAdapter.voice_mode(
    mode
)

print(
    "[TEST] HUD mode AFTER DIRECT ADAPTER:",
    hud.state.voice_mode
)

print()
print("=== TEST COMPLETE ===")