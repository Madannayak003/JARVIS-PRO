"""
=============================================================
JARVIS PRO — NATIVE DESKTOP HUD WINDOW
=============================================================

Native Windows window for the existing Next.js HUD.

The native window opens immediately.

Next.js HUD loading happens in the background.

Closing this window requests a full JARVIS shutdown.
"""

from __future__ import annotations

import os
import sys
import time
import threading
import urllib.request

import webview


HUD_URL = "http://127.0.0.1:3000"

WEBVIEW_STORAGE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "webview_data",
)

WINDOW_TITLE = "JARVIS PRO"

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 850

SHUTDOWN_URL = (
    "http://127.0.0.1:8766/shutdown"
)

# =============================================================
# GLOBAL NATIVE WINDOW
# =============================================================

_native_window = None


# =============================================================
# INITIAL LOADING SCREEN
# =============================================================

LOADING_HTML = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>JARVIS PRO</title>

<style>

html,
body {

    margin: 0;

    width: 100%;
    height: 100%;

    background: #050505;

    color: #f5a400;

    font-family:
        "Courier New",
        monospace;

    overflow: hidden;

}

.loading {

    width: 100%;
    height: 100%;

    display: flex;

    align-items: center;
    justify-content: center;

    flex-direction: column;

}

.title {

    font-size: 32px;

    letter-spacing: 8px;

    margin-bottom: 20px;

}

.status {

    font-size: 13px;

    letter-spacing: 3px;

    opacity: 0.75;

}

.dot {

    display: inline-block;

    animation:
        blink 1s infinite;

}

@keyframes blink {

    0% {
        opacity: 0.2;
    }

    50% {
        opacity: 1;
    }

    100% {
        opacity: 0.2;
    }

}

</style>

</head>


<body>

<div class="loading">

    <div class="title">
        JARVIS
    </div>

    <div class="status">

        INITIALIZING
        <span class="dot">...</span>

    </div>

</div>

</body>

</html>
"""


# =============================================================
# HUD READINESS CHECK
# =============================================================

def wait_for_hud(
    timeout: float = 30.0,
) -> bool:

    print(
        "[DESKTOP HUD] "
        "Waiting for Next.js HUD..."
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
                    "[DESKTOP HUD] "
                    "Next.js HUD is ready."
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


# =============================================================
# LOAD NEXT.JS IN BACKGROUND
# =============================================================

def _load_nextjs_when_ready(
    window,
    stop_event,
):

    if stop_event.is_set():

        return

    ready = wait_for_hud()

    if stop_event.is_set():

        return

    if not ready:

        print(
            "[DESKTOP HUD] "
            "Keeping loading screen because "
            "Next.js HUD is unavailable."
        )

        return

    try:

        print(
            "[DESKTOP HUD] "
            "Loading Next.js HUD into native window..."
        )

        window.load_url(
            HUD_URL
        )

        print(
            "[DESKTOP HUD] "
            "Next.js HUD loaded into native window."
        )

    except Exception as error:

        print(
            "[DESKTOP HUD] "
            "Could not load Next.js HUD:"
        )

        print(
            f"[DESKTOP HUD] {error}"
        )


# =============================================================
# SHUTDOWN
# =============================================================

def request_jarvis_shutdown():

    print(
        "[DESKTOP HUD] Window closed."
    )

    print(
        "[DESKTOP HUD] "
        "Requesting JARVIS shutdown..."
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

# =============================================================
# CLOSE NATIVE WINDOW
# =============================================================

def close_native_window():

    global _native_window

    window = _native_window

    if window is None:
        return

    try:

        print(
            "[DESKTOP HUD] "
            "Closing native JARVIS window..."
        )

        window.destroy()

    except Exception as error:

        print(
            "[DESKTOP HUD] "
            "Could not close native window:"
        )

        print(
            f"[DESKTOP HUD] {error}"
        )

# =============================================================
# NATIVE WINDOW
# =============================================================

def run():
    
    global _native_window

    # ---------------------------------------------------------
    # Stop signal for the background Next.js loader.
    # ---------------------------------------------------------

    stop_event = threading.Event()


    # =========================================================
    # CREATE NATIVE WINDOW IMMEDIATELY
    #
    # IMPORTANT:
    #
    # Do NOT wait for Next.js before creating this window.
    # =========================================================

    print(
        "[DESKTOP HUD] "
        "Creating native JARVIS window..."
    )


    _native_window = webview.create_window(

        WINDOW_TITLE,

        html=LOADING_HTML,

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
    
    window = _native_window


    # =========================================================
    # WINDOW CLOSED
    # =========================================================

    window.events.closed += (
        request_jarvis_shutdown
    )


    print(
        "[DESKTOP HUD] "
        "Native JARVIS window created."
    )


    # =========================================================
    # NEXT.JS LOADER
    #
    # Runs independently while pywebview is running.
    # =========================================================

    loader_thread = threading.Thread(

        target=_load_nextjs_when_ready,

        args=(
            window,
            stop_event,
        ),

        name="JARVIS-HUD-Loader",

        daemon=True,

    )

    loader_thread.start()


    print(
        "[DESKTOP HUD] "
        "Starting pywebview..."
    )


    # =========================================================
    # IMPORTANT
    #
    # pywebview stays on the MAIN THREAD.
    # =========================================================

    try:

        webview.start(
            debug=False,
            private_mode=False,
            storage_path=WEBVIEW_STORAGE_PATH,
        )

    finally:

        stop_event.set()
        
        _native_window = None


    print(
        "[DESKTOP HUD] "
        "Desktop HUD closed."
    )

    return 0


# =============================================================
# ENTRY POINT
# =============================================================

if __name__ == "__main__":

    sys.exit(
        run()
    )