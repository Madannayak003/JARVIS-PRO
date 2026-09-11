"""
=============================================================
JARVIS PRO — MAIN APPLICATION ENTRY POINT
=============================================================

Single-application desktop architecture.

JARVIS:
    - Runs the existing Python voice engine
    - Runs the existing HUD bridge
    - Starts Next.js silently
    - Displays the HUD through native pywebview
    - Does NOT open the HUD in a normal browser
    - Closing the native HUD shuts down JARVIS

IMPORTANT:
    pywebview.start() MUST run on the MAIN THREAD.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# =============================================================
# JARVIS CORE
# =============================================================

from skills.loader import load_all
from ai.memory import init_memory
from core.services import start_all
from core.core_state import mark_core_ready
from core.core_state import wait_for_core

from voice.mode import get_mode

from hud.integration import HUDIntegration
from hud.runtime import hud_runtime
from hud.web_bridge import hud_web

from dashboard.server import DashboardServer

# =============================================================
# GLOBAL STATE
# =============================================================

_web_hud_process = None
_voice_thread = None
_shutdown_event = threading.Event()
_shutdown_lock = threading.Lock()
_shutdown_started = False

# =============================================================
# PATHS
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
WEB_HUD_DIRECTORY = PROJECT_ROOT / "hud" / "web"
WEB_HUD_URL = "http://127.0.0.1:3000"


# =============================================================
# START NEXT.JS HUD
# =============================================================

def start_web_hud() -> bool:
    global _web_hud_process

    if _web_hud_process is not None and _web_hud_process.poll() is None:
        print("[MAIN HUD] Next.js HUD already running.")
        return True

    package_json = WEB_HUD_DIRECTORY / "package.json"

    if not package_json.is_file():
        print("[MAIN HUD] ERROR: HUD package.json not found.")
        print(f"[MAIN HUD] {package_json}")
        return False

    npm_command = "npm.cmd" if os.name == "nt" else "npm"

    log_directory = PROJECT_ROOT / "data" / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    web_log_path = log_directory / "hud_web.log"

    try:
        web_log = open(web_log_path, "a", encoding="utf-8", buffering=1)
        creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

        print("[MAIN HUD] Starting Next.js HUD...")

        _web_hud_process = subprocess.Popen(
            [npm_command, "run", "dev"],
            cwd=str(WEB_HUD_DIRECTORY),
            stdin=subprocess.DEVNULL,
            stdout=web_log,
            stderr=web_log,
            creationflags=creation_flags,
        )

        print("[MAIN HUD] Next.js HUD started.")
        print("[MAIN HUD] HUD URL:")
        print(WEB_HUD_URL)
        print(f"[MAIN HUD] Web logs: {web_log_path}")
        return True

    except FileNotFoundError:
        print("[MAIN HUD] ERROR: npm was not found.")
        return False
    except Exception as error:
        print(f"[MAIN HUD] Failed to start Next.js HUD: {error}")
        return False


# =============================================================
# WAIT FOR NEXT.JS
# =============================================================

def wait_for_web_hud(timeout: float = 30.0) -> bool:
    import urllib.request

    print("[MAIN HUD] Waiting for Next.js HUD...")
    started = time.time()

    while time.time() - started < timeout:
        if _shutdown_event.is_set():
            return False

        try:
            with urllib.request.urlopen(WEB_HUD_URL, timeout=1):
                print("[MAIN HUD] Next.js HUD is ready.")
                return True
        except Exception:
            time.sleep(0.25)

    print("[MAIN HUD] ERROR: Next.js HUD did not become ready.")
    return False


# =============================================================
# VOICE ENGINE
# =============================================================

def run_voice_engine():
    try:
        print("[MAIN] Voice engine waiting for core...")
        wait_for_core()

        if _shutdown_event.is_set():
            return

        print("[MAIN] Core ready. Starting voice engine...")
        from voice.online_runner import run

        print("[MAIN] Online JARVIS voice engine started.")
        run()

    except Exception as error:
        print(f"[MAIN] Voice engine stopped: {error}")
    finally:
        if not _shutdown_event.is_set():
            request_jarvis_shutdown()


def start_voice_engine():
    global _voice_thread

    _voice_thread = threading.Thread(
        target=run_voice_engine,
        name="jarvis-voice-engine",
        daemon=True,
    )
    _voice_thread.start()
    print("[MAIN] Voice engine thread started.")


# =============================================================
# SHUTDOWN
# =============================================================

def request_jarvis_shutdown():
    global _shutdown_started

    with _shutdown_lock:
        if _shutdown_started:
            return
        _shutdown_started = True

    print()
    print("[MAIN] Complete JARVIS shutdown requested.")
    _shutdown_event.set()

    # 1. Stop microphone listener
    try:
        from core.listener import request_shutdown
        request_shutdown()
    except Exception as error:
        print(f"[MAIN] Listener shutdown error: {error}")

    # 2. Close native pywebview HUD
    try:
        from hud.desktop_window import close_native_window
        close_native_window()
    except Exception as error:
        print(f"[MAIN HUD] Native window shutdown error: {error}")


# =============================================================
# HUD SHUTDOWN CALLBACK
# =============================================================

def configure_hud_shutdown():
    hud_web.set_shutdown_callback(request_jarvis_shutdown)
    print("[MAIN HUD] Desktop shutdown callback registered.")


# =============================================================
# START NATIVE HUD
# =============================================================

def start_native_hud():
    if not wait_for_web_hud():
        return False

    print("[MAIN HUD] Opening JARVIS desktop window...")

    try:
        from hud.desktop_window import run

        # pywebview requires the MAIN THREAD.
        result = run()
        print(f"[MAIN HUD] Desktop HUD exited: {result}")

        if not _shutdown_event.is_set():
            request_jarvis_shutdown()

        return True

    except Exception as error:
        print(f"[MAIN HUD] Native HUD failed: {error}")
        request_jarvis_shutdown()
        return False


# =============================================================
# STOP NEXT.JS (INSTANT PROCESS TREE TERMINATION)
# =============================================================

def stop_web_hud():
    global _web_hud_process

    process = _web_hud_process
    _web_hud_process = None

    if process is None:
        return

    try:
        if process.poll() is None:
            print("[MAIN HUD] Stopping Next.js HUD...")

            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                process.terminate()

            print("[MAIN HUD] Next.js HUD stopped.")

    except Exception as error:
        print(f"[MAIN HUD] Next.js cleanup error: {error}")


# =============================================================
# BACKGROUND CORE INITIALIZATION
# =============================================================

def initialize_core_background():
    try:
        print("[CORE] Background initialization started.")
        print("[CORE] Loading skills...")
        load_all()

        print("[CORE] Initializing memory...")
        init_memory()

        print("[CORE] Starting services...")
        start_all()

        print("[CORE] Background initialization complete.")
        mark_core_ready()

    except Exception as error:
        print(f"[CORE] Background initialization failed: {error}")
        raise


# =============================================================
# MAIN
# =============================================================

def main():
    try:
        mode = get_mode()
        print(f"[MAIN] Voice mode: {mode}")

        HUDIntegration.voice_mode(mode)
        print(f"[MAIN HUD] Voice mode sent to HUD: {mode}")

        if mode == "offline":
            print("[MAIN] Starting isolated offline JARVIS...")
            from voice.offline.offline_runner import run
            return run()

        print("[MAIN] Starting existing online JARVIS...")

        core_thread = threading.Thread(
            target=initialize_core_background,
            name="jarvis-core-init",
            daemon=True,
        )
        core_thread.start()
        print("[MAIN] Core initialization started in background.")

        hud_runtime.start()
        print("[MAIN HUD] HUD runtime started.")

        if not hud_web.start():
            print("[MAIN HUD] WARNING: HUD bridge failed.")
        else:
            print("[MAIN HUD] Web HUD bridge started.")

        configure_hud_shutdown()

        if not start_web_hud():
            print("[MAIN HUD] Next.js HUD failed to start.")
            return 1

        # Register live conversation actions
        from core.registry import register
        from voice.live_conversation import (
            start_live_conversation,
            stop_live_conversation,
            live_conversation_status,
        )

        register("start_live_conversation", start_live_conversation, category="voice")
        register("stop_live_conversation", stop_live_conversation, category="voice")
        register("live_conversation_status", live_conversation_status, category="voice")
        print("[LIVE] Live Conversation actions registered.")

        # Remote dashboard
        from core.dispatcher import dispatch

        remote_server = DashboardServer(
            command_handler=dispatch,
            live_stop_handler=stop_live_conversation,
        )
        remote_server.new_pairing_pin()

        if remote_server.start():
            print(f"[REMOTE] JARVIS Dashboard: {remote_server.url()}")
            print(f"[REMOTE] Pairing PIN: {remote_server._pin}")
            print("[REMOTE] Dashboard Live stop control: READY")

        start_voice_engine()

        print("[MAIN HUD] Starting native JARVIS HUD...")
        start_native_hud()

        print("[MAIN] Native HUD closed.")
        request_jarvis_shutdown()

        # Instant check instead of hanging on join
        if _voice_thread is not None and _voice_thread.is_alive():
            _voice_thread.join(timeout=0.5)

        return 0

    except KeyboardInterrupt:
        print("\n[MAIN] Shutdown requested.")
        request_jarvis_shutdown()
        return 0

    finally:
        print("[MAIN] Cleaning up JARVIS...")

        try:
            from core.listener import stop_listener
            stop_listener()
        except Exception:
            pass

        try:
            hud_web.stop()
        except Exception:
            pass

        stop_web_hud()

        print("[MAIN] JARVIS shutdown complete.")
        # Instantly releases terminal prompt without socket/thread hanging
        os._exit(0)


# =============================================================
# ENTRY POINT
# =============================================================

if __name__ == "__main__":
    sys.exit(main() or 0)