"""
JARVIS PRO
HUD Telemetry Test
"""

from hud.telemetry import telemetry


print()
print("=== HUD TELEMETRY TEST ===")
print()

print(
    "[HUD TELEMETRY] Available:",
    telemetry.available()
)

print(
    "[HUD TELEMETRY] CPU:",
    telemetry.get_cpu()
)

print(
    "[HUD TELEMETRY] RAM:",
    telemetry.get_ram()
)

print(
    "[HUD TELEMETRY] BATTERY:",
    telemetry.get_battery()
)

print()

data = telemetry.read()

print(
    "[HUD TELEMETRY] Full:",
    data
)

print()
print("=== TELEMETRY TEST COMPLETE ===")