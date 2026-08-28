"""
=============================================================
JARVIS PRO — NATIVE DESKTOP HUD WINDOW
=============================================================

Native Windows window for the existing Next.js HUD.

The Next.js HUD is displayed inside pywebview.
Closing this window requests a full JARVIS shutdown.
"""

from __future__ import annotations

import sys
import time
import urllib.request

import webview


HUD_URL = "http://127.0.0.1:3000"

WINDOW_TITLE = "JARVIS PRO"

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 850


SHUTDOWN_URL = (
    "http://127.0.0.1:8766/shutdown"
)


def wait_for_hud(
    timeout: float = 30.0,
) -> bool:

    print(
        "[DESKTOP HUD] Waiting for Next.js HUD..."
    )

    start = time.time()

    while (
        time.time() - start
        < timeout
    ):

        try:

            with urllib.request.urlopen(
                HUD_URL,
                timeout=1,
            ):

                print(
                    "[DESKTOP HUD] Next.js HUD is ready."
                )

                return True

        except Exception:

            time.sleep(
                0.25
            )

    print(
        "[DESKTOP HUD] ERROR: "
        "Next.js HUD did not start."
    )

    return False


def request_jarvis_shutdown():

    print(
        "[DESKTOP HUD] Window closed."
    )

    print(
        "[DESKTOP HUD] Requesting JARVIS shutdown..."
    )

    try:

        request = urllib.request.Request(
            SHUTDOWN_URL,
            method="POST",
        )

        urllib.request.urlopen(
            request,
            timeout=1,
        )

        print(
            "[DESKTOP HUD] "
            "JARVIS shutdown requested."
        )

    except Exception as error:

        print(
            "[DESKTOP HUD] "
            "Could not request shutdown:"
        )

        print(
            f"[DESKTOP HUD] {error}"
        )


def run():

    if not wait_for_hud():

        return 1


    print(
        "[DESKTOP HUD] Creating native JARVIS window..."
    )


    window = webview.create_window(

        WINDOW_TITLE,

        HUD_URL,

        width=WINDOW_WIDTH,

        height=WINDOW_HEIGHT,

        min_size=(
            1000,
            650,
        ),

        resizable=True,

        text_select=False,

        zoomable=False,

    )


    # =========================================================
    # WINDOW CLOSED
    # =========================================================

    window.events.closed += (
        request_jarvis_shutdown
    )


    print(
        "[DESKTOP HUD] Native JARVIS window created."
    )

    print(
        "[DESKTOP HUD] Starting pywebview..."
    )


    webview.start(
        debug=False,
    )


    print(
        "[DESKTOP HUD] Desktop HUD closed."
    )

    return 0


if __name__ == "__main__":

    sys.exit(
        run()
    )