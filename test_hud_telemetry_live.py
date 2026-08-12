"""
JARVIS PRO
Live HUD Telemetry Test
"""

import time

from hud.telemetry import telemetry


print()
print("=== LIVE HUD TELEMETRY TEST ===")
print()
print("Press Ctrl+C to stop.")
print()

try:

    while True:

        data = telemetry.read()

        cpu = data["cpu"]
        ram = data["ram"]
        battery = data["battery"]

        print(
            f"CPU: {cpu}% | "
            f"RAM: {ram}% | "
            f"BATTERY: {battery}%"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print()
    print("=== TELEMETRY TEST STOPPED ===")