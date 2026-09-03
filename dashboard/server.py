"""
=============================================================
JARVIS PRO — DASHBOARD SERVER
=============================================================

Mark Remote Dashboard adapted for JARVIS PRO.

Architecture:

    Phone
       ↓
    Dashboard
       ↓
    core.dispatcher.dispatch()
       ↓
    NCI / Fast Router / Skills

This server does NOT create another JARVIS brain.

Features:

    - 6-character pairing PIN
    - Multiple authenticated sessions
    - Device auto-reconnect
    - AES-256-CBC command encryption
    - WebSocket dashboard
    - Command/event history
    - File upload
    - File download
    - Phone microphone WebSocket queue
    - Direct Live Conversation stop
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import secrets
import socket
import threading
import time

from pathlib import Path
from typing import Callable, Optional

import json

from core.runtime import handle_priority

from hud.integration import HUDIntegration

from tools.windows_integration import (
    get_autostart_status,
    set_autostart,
)

from core.listener import (
    start_listener,
    pause_listener,
    resume_listener,
    listener_running,
    listener_paused,
)

# =============================================================
# ROBUST DESKTOP SHORTCUT BUILDER (WINDOWS / LINUX)
# =============================================================

def create_desktop_shortcut() -> str:
    """
    Creates a clean desktop shortcut with the exact working directory 
    set to your Jarvis project path, using pythonw.exe to stay windowless.
    """
    import sys
    import os

    desktop_path = None
    if os.name == "nt":
        try:
            import winreg
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
        except Exception:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    if not desktop_path or not os.path.exists(desktop_path):
        os.makedirs(desktop_path, exist_ok=True)

    # Get absolute path to main.py instead of sys.argv[0] so shortcut always boots the core
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_script = os.path.join(project_dir, "main.py")
    icon_path = os.path.join(project_dir, "config", "jarvis.ico")
    
    pythonw_executable = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw_executable):
        pythonw_executable = sys.executable

    if os.name == "nt":
        shortcut_path = os.path.join(desktop_path, "Jarvis Pro.lnk")
        powershell_script = (
            f"$WshShell = New-Object -ComObject WScript.Shell; "
            f"$Shortcut = $WshShell.CreateShortcut('{shortcut_path}'); "
            f"$Shortcut.TargetPath = '{pythonw_executable}'; "
            f"$Shortcut.Arguments = '\"{target_script}\"'; "
            f"$Shortcut.WorkingDirectory = '{project_dir}'; "  # Forces correct project path context
            f"$Shortcut.WindowStyle = 7; "
        )
        if os.path.exists(icon_path):
            powershell_script += f"$Shortcut.IconLocation = '{icon_path}'; "
        powershell_script += "$Shortcut.Save()"

        import subprocess
        subprocess.run(["powershell", "-Command", powershell_script], check=True)
        return "Windows desktop shortcut created successfully."
    else:
        shortcut_path = os.path.join(desktop_path, "Jarvis-Pro.desktop")
        desktop_entry = (
            f"[Desktop Entry]\n"
            f"Type=Application\n"
            f"Name=Jarvis Pro\n"
            f"Exec={pythonw_executable} \"{target_script}\"\n"
            f"Path={project_dir}\n"
            f"Terminal=false\n"
        )
        if os.path.exists(icon_path):
            desktop_entry += f"Icon={icon_path}\n"
        
        with open(shortcut_path, "w", encoding="utf-8") as f:
            f.write(desktop_entry)
        os.chmod(shortcut_path, 0o755)
        return "Linux desktop shortcut created successfully."


# =============================================================
# FASTAPI
# =============================================================

try:

    from fastapi import (
        FastAPI,
        File,
        Request,
        UploadFile,
        WebSocket,
        WebSocketDisconnect,
    )

    from fastapi.middleware.cors import CORSMiddleware

    from fastapi.responses import (
        FileResponse,
        HTMLResponse,
        JSONResponse,
    )

    from fastapi.staticfiles import StaticFiles

    import uvicorn

    FASTAPI_AVAILABLE = True

except ImportError:

    FastAPI = None
    File = None
    Request = None
    UploadFile = None
    WebSocket = None
    WebSocketDisconnect = None

    FileResponse = None
    HTMLResponse = None
    JSONResponse = None

    StaticFiles = None
    uvicorn = None

    FASTAPI_AVAILABLE = False


# =============================================================
# MULTIPART
# =============================================================

try:

    import multipart

    MULTIPART_AVAILABLE = True

except ImportError:

    MULTIPART_AVAILABLE = False


# =============================================================
# PATHS / CONFIGURATION
# =============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

STATIC_DIR = (
    Path(__file__)
    .resolve()
    .parent
    / "static"
)

STATIC_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


PORT = 8765

PIN_EXPIRY_SECONDS = 600

MAX_UPLOAD_MB = 500

PIN_CHARS = (
    "ABCDEFGHJKMNPQRSTUVWXYZ"
    "23456789"
)

AES_SALT = (
    b"JARVIS-DASHBOARD-v1"
)


# =============================================================
# UPLOAD DIRECTORY
# =============================================================

def _make_uploads_dir() -> Path:

    candidates = (

        Path.home()
        / "Downloads"
        / "JARVIS Uploads",

        Path.home()
        / "Documents"
        / "JARVIS Uploads",

        BASE_DIR
        / "uploads",
    )

    for candidate in candidates:

        try:

            candidate.mkdir(
                parents=True,
                exist_ok=True,
            )

            return candidate

        except Exception:

            pass

    fallback = (
        BASE_DIR
        / "uploads"
    )

    fallback.mkdir(
        parents=True,
        exist_ok=True,
    )

    return fallback


UPLOADS_DIR = (
    _make_uploads_dir()
)


# =============================================================
# LOCAL IP
# =============================================================

def _local_ip() -> str:
    """
    Find the LAN IP used by JARVIS.

    This does not send application data.
    It only asks Windows which local interface
    would be used for the UDP route.
    """

    for probe in (
        "8.8.8.8",
        "1.1.1.1",
        "192.168.1.1",
    ):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        try:

            sock.settimeout(0.5)

            sock.connect(
                (
                    probe,
                    80,
                )
            )

            ip = (
                sock
                .getsockname()[0]
            )

            if not ip.startswith(
                "127."
            ):

                return ip

        except Exception:

            pass

        finally:

            sock.close()

    # ---------------------------------------------------------
    # Fallback
    # ---------------------------------------------------------

    try:

        ip = socket.gethostbyname(
            socket.gethostname()
        )

        if not ip.startswith(
            "127."
        ):

            return ip

    except Exception:

        pass

    return "127.0.0.1"


# =============================================================
# STATIC FILES
# =============================================================

def _read_static(
    filename: str,
) -> str:

    path = (
        STATIC_DIR
        / filename
    )

    return path.read_text(
        encoding="utf-8"
    )


# =============================================================
# AES-256
# =============================================================

def _derive_key(
    session_key: str,
) -> bytes:

    return hashlib.sha256(
        session_key.encode(
            "utf-8"
        )
        + AES_SALT
    ).digest()


def _decrypt_cbc(
    aes_key: bytes,
    encrypted: str,
) -> str:

    from cryptography.hazmat.primitives.ciphers import (
        Cipher,
        algorithms,
        modes,
    )

    from cryptography.hazmat.primitives import (
        padding,
    )

    raw = base64.b64decode(
        encrypted
    )

    if len(raw) < 32:

        raise ValueError(
            "Invalid encrypted payload."
        )

    iv = raw[:16]

    ciphertext = raw[16:]

    decryptor = Cipher(
        algorithms.AES(
            aes_key
        ),
        modes.CBC(
            iv
        ),
    ).decryptor()

    padded = (
        decryptor.update(
            ciphertext
        )
        + decryptor.finalize()
    )

    unpadder = (
        padding.PKCS7(
            128
        ).unpadder()
    )

    plaintext = (
        unpadder.update(
            padded
        )
        + unpadder.finalize()
    )

    return plaintext.decode(
        "utf-8"
    )


# =============================================================
# DASHBOARD SERVER
# =============================================================

class DashboardServer:

    def __init__(
        self,
        command_handler: Optional[
            Callable[[str], object]
        ] = None,

        live_stop_handler: Optional[
            Callable[..., object]
        ] = None,

        port: int = PORT,
    ):

        # -----------------------------------------------------
        # Existing JARVIS dispatcher
        # -----------------------------------------------------

        self.command_handler = (
            command_handler
        )

        # -----------------------------------------------------
        # Direct Live Conversation stop
        # -----------------------------------------------------

        self.live_stop_handler = (
            live_stop_handler
        )

        # -----------------------------------------------------
        # Network
        # -----------------------------------------------------

        self.port = int(
            port
        )

        self.ip = _local_ip()

        # -----------------------------------------------------
        # Pairing
        # -----------------------------------------------------

        self._pin = None

        self._pin_expiry = 0.0

        # -----------------------------------------------------
        # Authentication
        #
        # token -> session key
        # -----------------------------------------------------

        self._tokens = set()

        self._token_keys = {}

        # -----------------------------------------------------
        # Persistent device sessions
        #
        # device token -> session information
        # -----------------------------------------------------

        self._device_sessions = {}

        # -----------------------------------------------------
        # WebSocket clients
        # -----------------------------------------------------

        self._clients = set()

        # -----------------------------------------------------
        # Dashboard history
        # -----------------------------------------------------

        self._history = []

        # -----------------------------------------------------
        # Phone audio
        #
        # This queue will later be connected to the
        # existing JARVIS Live Conversation engine.
        # -----------------------------------------------------

        self._phone_audio_queue = (
            asyncio.Queue(
                maxsize=200
            )
        )

        # -----------------------------------------------------
        # Async event loop
        # -----------------------------------------------------

        self._loop = None

        # -----------------------------------------------------
        # Server thread
        # -----------------------------------------------------

        self._thread = None

        # -----------------------------------------------------
        # HTML
        # -----------------------------------------------------

        self._login_html = (
            _read_static(
                "login.html"
            )
        )

        self._app_html = (
            _read_static(
                "app.html"
            )
        )

        # -----------------------------------------------------
        # FastAPI
        # -----------------------------------------------------

        self.app = (

            self._build_app()

            if FASTAPI_AVAILABLE

            else None
        )
        
        # -----------------------------------------------------
        # Connect JARVIS voice output to Remote Dashboard
        # -----------------------------------------------------

        try:

            from voice.manager import (
                add_speech_listener
            )

            add_speech_listener(
                self._on_voice_output
            )

            print(
                "[REMOTE] Voice output bridge connected."
            )

        except Exception as e:

            print(
                "[REMOTE] Voice output bridge failed:",
                e
            )
            
    # =========================================================
    # JARVIS VOICE OUTPUT → HUD + REMOTE DASHBOARD
    # =========================================================

    def _on_voice_output(
        self,
        text: str,
    ):

        if not text:
            return

        text = str(text).strip()

        if not text:
            return

        print(
            "[REMOTE VOICE] Sending:",
            text,
        )

        # -----------------------------------------------------
        # HUD Activity Log
        #
        # This records the actual JARVIS response.
        # It does NOT control voice playback.
        # -----------------------------------------------------

        try:

            from hud.integration import (
                HUDIntegration
            )

            HUDIntegration.response(
                text
            )

        except Exception as exc:

            print(
                "[HUD RESPONSE LOG] Failed:",
                exc
            )

        # -----------------------------------------------------
        # Existing Mark-style Remote Dashboard
        # -----------------------------------------------------

        self._broadcast_threadsafe({

            "type": "log",

            "speaker": "jarvis",

            "text": text,

            "ts": time.time(),

        })

    # =========================================================
    # PAIRING PIN
    # =========================================================

    def new_pairing_pin(
        self,
        expiry_seconds: int = (
            PIN_EXPIRY_SECONDS
        ),
    ) -> str:

        self._pin = "".join(

            secrets.choice(
                PIN_CHARS
            )

            for _ in range(6)
        )

        self._pin_expiry = (
            time.time()
            + int(
                expiry_seconds
            )
        )

        # -----------------------------------------------------
        # New pairing invalidates current sessions.
        # -----------------------------------------------------

        self._tokens.clear()

        self._token_keys.clear()

        print(
            "[REMOTE] New pairing PIN generated."
        )

        return self._pin

    # =========================================================
    # URL
    # =========================================================

    def url(self) -> str:

        return (
            f"http://"
            f"{self.ip}:"
            f"{self.port}"
        )

    # =========================================================
    # PAIRING URL
    # =========================================================

    def pairing_url(self) -> str:

        return (
            f"{self.url()}"
            f"/login"
            f"?pin={self._pin or ''}"
        )

    # =========================================================
    # AUTH
    # =========================================================

    def _get_token(
        self,
        request: Request,
    ) -> Optional[str]:

        auth = request.headers.get(
            "authorization",
            "",
        )

        token = (
            auth
            .removeprefix(
                "Bearer "
            )
            .strip()
        )

        if token in self._tokens:

            return token

        return None

    def _authorize(
        self,
        request: Request,
    ) -> bool:

        return (
            self._get_token(
                request
            )
            is not None
        )
        
    # =========================================================
    # LOCAL CONTROL AUTHORIZATION
    # =========================================================

    def _authorize_local(
        self,
        request: Request,
    ) -> bool:
        """
        Allow local JARVIS HUD controls only from this PC.

        Remote phones/devices must not be able to create
        Windows shortcuts or modify Windows startup.
        """

        client = request.client

        if client is None:
            return False

        host = client.host

        return host in {
            "127.0.0.1",
            "::1",
            self.ip,
        }

    # =========================================================
    # BROADCAST
    # =========================================================

    async def broadcast(
        self,
        message: dict,
    ):

        self._history.append(
            message
        )

        if len(
            self._history
        ) > 300:

            self._history = (
                self._history[-300:]
            )

        dead = set()

        for client in list(
            self._clients
        ):

            try:

                await client.send_json(
                    message
                )

            except Exception:

                dead.add(
                    client
                )

        self._clients.difference_update(
            dead
        )

    # =========================================================
    # THREADSAFE BROADCAST
    # =========================================================

    def _broadcast_threadsafe(
        self,
        message: dict,
    ):

        if self._loop is None:

            return

        try:

            asyncio.run_coroutine_threadsafe(

                self.broadcast(
                    message
                ),

                self._loop,
            )

        except Exception:

            pass

    # =========================================================
    # REMOTE COMMAND
    # =========================================================

    def _run_command(
        self,
        text: str,
    ):

        print(
            "[REMOTE COMMAND] Received:",
            text,
        )

        self._broadcast_threadsafe({
            "type": "log",
            "speaker": "user",
            "text": text,
        })

        # =====================================================
        # PRIORITY INTERRUPT
        #
        # "stop conversation" means:
        # stop the current response/task.
        #
        # It does NOT stop Live Conversation.
        # =====================================================

        try:

            if handle_priority(text):

                self._broadcast_threadsafe({
                    "type": "log",
                    "speaker": "jarvis",
                    "text": "Stopped.",
                })

                return

        except Exception as exc:

            print(
                "[REMOTE INTERRUPT ERROR]",
                exc,
            )

            self._broadcast_threadsafe({
                "type": "sys",
                "text": (
                    f"Interrupt error: {exc}"
                ),
            })

            return

        # =====================================================
        # NORMAL COMMAND
        # =====================================================

        if not self.command_handler:

            print(
                "[REMOTE COMMAND] "
                "ERROR: dispatcher not connected."
            )

            self._broadcast_threadsafe({
                "type": "sys",
                "text": (
                    "JARVIS dispatcher "
                    "is not connected."
                ),
            })

            return

        try:

            result = (
                self.command_handler(
                    text
                )
            )

            if result is not None:

                result_text = str(
                    result
                ).strip()

                if result_text:

                    self._broadcast_threadsafe({
                        "type": "log",
                        "speaker": "jarvis",
                        "text": result_text,
                    })

        except Exception as exc:

            print(
                "[REMOTE COMMAND ERROR]",
                exc,
            )

            self._broadcast_threadsafe({
                "type": "sys",
                "text": (
                    f"Command error: {exc}"
                ),
            })

    # =========================================================
    # BUILD FASTAPI
    # =========================================================

    def _build_app(
        self,
    ):

        app = FastAPI(
            docs_url=None,
            redoc_url=None,
        )

        # -----------------------------------------------------
        # CORS
        #
        # The JARVIS PRO HUD runs on Next.js
        # while the remote dashboard runs on Python.
        # -----------------------------------------------------

        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://127.0.0.1:3000",

                # JARVIS PRO HUD opened through the LAN address.
                f"http://{self.ip}:3000",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # -----------------------------------------------------
        # Static files
        # -----------------------------------------------------

        if StaticFiles:

            app.mount(
                "/static",
                StaticFiles(
                    directory=str(
                        STATIC_DIR
                    )
                ),
                name="static",
            )

        # -----------------------------------------------------
        # CryptoJS compatibility
        #
        # app.html expects:
        #
        #     /static/crypto.js
        #
        # Mark's folder contains:
        #
        #     crypto-js.min.js
        #
        # So expose the same file under crypto.js.
        # -----------------------------------------------------

        @app.get(
            "/static/crypto.js"
        )
        async def crypto_js():

            crypto_file = (
                STATIC_DIR
                / "crypto-js.min.js"
            )

            if not crypto_file.exists():

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "crypto-js.min.js "
                            "is missing."
                        ),
                    },
                    status_code=404,
                )

            return FileResponse(
                str(
                    crypto_file
                ),
                media_type=(
                    "application/javascript"
                ),
            )

        # =====================================================
        # LOGIN PAGE
        # =====================================================

        @app.get(
            "/login",
            response_class=HTMLResponse,
        )
        async def login_page():

            return HTMLResponse(
                self._login_html
            )

        # =====================================================
        # DASHBOARD
        # =====================================================

        @app.get(
            "/",
            response_class=HTMLResponse,
        )
        async def index():

            html = (
                self._app_html
                .replace(
                    "__IP__",
                    self.ip,
                )
                .replace(
                    "__PORT__",
                    str(
                        self.port
                    ),
                )
            )

            return HTMLResponse(
                html
            )

        # =====================================================
        # LOGIN
        # =====================================================

        @app.post(
            "/login"
        )
        async def login(
            request: Request,
        ):

            self._loop = (
                asyncio.get_running_loop()
            )

            try:

                body = (
                    await request.json()
                )

            except Exception:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Invalid request."
                        ),
                    },
                    status_code=400,
                )

            entered = str(
                body.get(
                    "pin",
                    "",
                )
            ).strip().upper()

            # -------------------------------------------------
            # Validate PIN
            # -------------------------------------------------

            if (
                not self._pin
                or time.time()
                > self._pin_expiry
                or entered
                != self._pin
            ):

                print(
                    "[REMOTE LOGIN] "
                    "Invalid or expired PIN."
                )

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Invalid or expired key."
                        ),
                    },
                    status_code=401,
                )

            # -------------------------------------------------
            # Create session
            # -------------------------------------------------

            session_key = (
                secrets.token_urlsafe(
                    32
                )
            )

            token = (
                secrets.token_urlsafe(
                    32
                )
            )

            device_token = (
                secrets.token_urlsafe(
                    32
                )
            )

            self._tokens.add(
                token
            )

            self._token_keys[
                token
            ] = session_key

            self._device_sessions[
                device_token
            ] = {
                "session_key":
                    session_key,

                "created_at":
                    time.time(),
            }

            remaining = max(
                0,
                int(
                    self._pin_expiry
                    - time.time()
                ),
            )

            print(
                "[REMOTE LOGIN] SUCCESS."
            )

            print(
                "[REMOTE LOGIN] "
                "Remote device authenticated."
            )

            print(
                "[REMOTE LOGIN] "
                f"PIN remaining: {remaining}s"
            )

            await self.broadcast({
                "type": "sys",
                "text": (
                    "Remote device connected."
                ),
            })

            return {
                "ok": True,
                "token": token,
                "key": session_key,
                "device_token":
                    device_token,
            }

        # =====================================================
        # DEVICE AUTO LOGIN
        # =====================================================

        @app.post(
            "/api/device-login"
        )
        async def device_login(
            request: Request,
        ):

            self._loop = (
                asyncio.get_running_loop()
            )

            try:

                body = (
                    await request.json()
                )

            except Exception:

                return JSONResponse(
                    {
                        "ok": False
                    },
                    status_code=400,
                )

            device_token = str(
                body.get(
                    "device_token",
                    "",
                )
            ).strip()

            device = (
                self._device_sessions.get(
                    device_token
                )
            )

            if not device:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Device session "
                            "not found."
                        ),
                    },
                    status_code=401,
                )

            session_key = (
                device[
                    "session_key"
                ]
            )

            token = (
                secrets.token_urlsafe(
                    32
                )
            )

            self._tokens.add(
                token
            )

            self._token_keys[
                token
            ] = session_key

            print(
                "[REMOTE] "
                "Known device reconnected."
            )

            await self.broadcast({
                "type": "sys",
                "text": (
                    "Known device "
                    "reconnected automatically."
                ),
            })

            return {
                "ok": True,
                "token": token,
                "key": session_key,
            }

        # =====================================================
        # INFO
        # =====================================================

        @app.get(
            "/api/info"
        )
        async def info():

            pairing_active = (
                bool(self._pin)
                and
                time.time()
                < self._pin_expiry
            )

            return {
                "ok": True,

                "url": self.url(),

                "pairing_url": (
                    self.pairing_url()
                    if pairing_active
                    else ""
                ),

                "pairing_pin": (
                    self._pin
                    if pairing_active
                    else ""
                ),

                "pairing_active": pairing_active,

                "clients": len(
                    self._clients
                ),
            }
            
        # =====================================================
        # LOCAL — DESKTOP SHORTCUT
        # =====================================================

        @app.post(
            "/api/local/shortcut"
        )
        async def local_shortcut(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Local access required.",
                    },
                    status_code=403,
                )

            try:

                result = create_desktop_shortcut()

                return {
                    "ok": True,
                    "message": result,
                }

            except Exception as exc:

                print(
                    "[LOCAL SHORTCUT ERROR]",
                    exc,
                )

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(exc),
                    },
                    status_code=500,
                )


        # =====================================================
        # LOCAL — AUTO START STATUS
        # =====================================================

        @app.get(
            "/api/local/autostart"
        )
        async def local_autostart_status(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Local access required.",
                    },
                    status_code=403,
                )

            try:

                enabled = get_autostart_status()

                return {
                    "ok": True,
                    "enabled": enabled,
                }

            except Exception as exc:

                print(
                    "[LOCAL AUTOSTART STATUS ERROR]",
                    exc,
                )

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(exc),
                    },
                    status_code=500,
                )


        # =====================================================
        # LOCAL — AUTO START SET
        # =====================================================

        @app.post(
            "/api/local/autostart"
        )
        async def local_autostart(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Local access required.",
                    },
                    status_code=403,
                )

            try:

                body = await request.json()

            except Exception:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Invalid request.",
                    },
                    status_code=400,
                )

            enabled = bool(
                body.get(
                    "enabled",
                    False,
                )
            )

            try:

                result = set_autostart(
                    enabled
                )

                return {
                    "ok": True,
                    "enabled": enabled,
                    "message": result,
                }

            except Exception as exc:

                print(
                    "[LOCAL AUTOSTART ERROR]",
                    exc,
                )

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(exc),
                    },
                    status_code=500,
                )
                
        # =====================================================
        # LOCAL — MICROPHONE STATUS
        # =====================================================

        @app.get(
            "/api/local/microphone"
        )
        async def local_microphone_status(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Local access required.",
                    },
                    status_code=403,
                )

            try:

                running = listener_running()
                paused = listener_paused()

                return {
                    "ok": True,
                    "enabled": (
                        running
                        and not paused
                    ),
                    "running": running,
                    "paused": paused,
                }

            except Exception as exc:

                print(
                    "[LOCAL MICROPHONE STATUS ERROR]",
                    exc,
                )

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(exc),
                    },
                    status_code=500,
                )


        # =====================================================
        # LOCAL — MICROPHONE SET
        # =====================================================

        @app.post(
            "/api/local/microphone"
        )
        async def local_microphone(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Local access required.",
                    },
                    status_code=403,
                )

            try:

                body = await request.json()

            except Exception:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Invalid request.",
                    },
                    status_code=400,
                )

            enabled = bool(
                body.get(
                    "enabled",
                    False,
                )
            )

            try:

                from voice.live_conversation import _live

            except Exception:

                _live = None

            if _live is not None and _live.running:

                _live.set_microphone_enabled(
                    enabled
                )

                actual_enabled = (
                    _live.microphone_enabled()
                )

                running = True

                paused = not actual_enabled

            else:

                if enabled:

                    if not listener_running():

                        start_listener()

                    elif listener_paused():

                        resume_listener()

                else:

                    pause_listener()

                running = listener_running()

                paused = listener_paused()

                actual_enabled = (
                    running
                    and not paused
                )

            print(
                "[LOCAL MICROPHONE]",
                "ON" if actual_enabled else "OFF",
            )

            try:

                HUDIntegration.system_activity(
                    "MICROPHONE "
                    + (
                        "ON"
                        if actual_enabled
                        else "OFF"
                    )
                )

            except Exception as exc:

                print(
                    "[HUD MICROPHONE LOG ERROR]",
                    exc,
                )

            return {
                "ok": True,
                "enabled": actual_enabled,
                "running": running,
                "paused": paused,
            }
                
        # =====================================================
        # LOCAL — MORNING BRIEF STATUS
        # =====================================================

        @app.get(
            "/api/local/morning-brief"
        )
        async def local_morning_brief_status(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Local access required.",
                    },
                    status_code=403,
                )

            settings_file = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "settings"
                / "jarvis_settings.json"
            )

            try:

                if not settings_file.exists():

                    return {
                        "ok": True,
                        "enabled": True,
                    }

                with settings_file.open(
                    "r",
                    encoding="utf-8",
                ) as file:

                    settings = json.load(file)

                return {
                    "ok": True,
                    "enabled": bool(
                        settings.get(
                            "morningBrief",
                            True,
                        )
                    ),
                }

            except Exception as exc:

                print(
                    "[LOCAL MORNING BRIEF STATUS ERROR]",
                    exc,
                )

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(exc),
                    },
                    status_code=500,
                )


        # =====================================================
        # LOCAL — MORNING BRIEF SET
        # =====================================================

        @app.post(
            "/api/local/morning-brief"
        )
        async def local_morning_brief(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Local access required.",
                    },
                    status_code=403,
                )

            try:

                body = await request.json()

            except Exception:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": "Invalid request.",
                    },
                    status_code=400,
                )

            enabled = bool(
                body.get(
                    "enabled",
                    False,
                )
            )
            
            try:

                HUDIntegration.system_activity(
                    "MORNING BRIEF "
                    + (
                        "ON"
                        if enabled
                        else "OFF"
                    )
                )

            except Exception as exc:

                print(
                    "[HUD MORNING BRIEF LOG ERROR]",
                    exc,
                )

            settings_file = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "settings"
                / "jarvis_settings.json"
            )

            try:

                settings_file.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                settings = {}

                if settings_file.exists():

                    try:

                        with settings_file.open(
                            "r",
                            encoding="utf-8",
                        ) as file:

                            settings = json.load(file)

                    except Exception:

                        settings = {}

                settings["morningBrief"] = enabled

                with settings_file.open(
                    "w",
                    encoding="utf-8",
                ) as file:

                    json.dump(
                        settings,
                        file,
                        indent=2,
                    )

                    file.write("\n")

                print(
                    "[LOCAL MORNING BRIEF] "
                    f"Set to {'ON' if enabled else 'OFF'}"
                )

                return {
                    "ok": True,
                    "enabled": enabled,
                }

            except Exception as exc:

                print(
                    "[LOCAL MORNING BRIEF ERROR]",
                    exc,
                )

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(exc),
                    },
                    status_code=500,
                )
                
        # =====================================================
        # LOCAL — CUSTOMISE SETTINGS (NAME & COLOUR)
        # =====================================================

        @app.get(
            "/api/local/customise"
        )
        async def local_get_customise(
            request: Request,
        ):
            if not self._authorize_local(request):
                return JSONResponse(
                    {"ok": False, "error": "Local access required."},
                    status_code=403,
                )

            settings_file = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "settings"
                / "jarvis_settings.json"
            )

            try:
                if not settings_file.exists():
                    return {
                        "ok": True,
                        "assistantName": "JARVIS",
                        "userName": "MADAN.R",
                        "assistantColour": "#ffaa30",
                    }

                with settings_file.open("r", encoding="utf-8") as f:
                    settings = json.load(f)

                return {
                    "ok": True,
                    "assistantName": settings.get("assistantName", "JARVIS"),
                    "userName": settings.get("userName", "MADAN.R"),
                    "assistantColour": settings.get("assistantColour", "#ffaa30"),
                }
            except Exception as exc:
                return JSONResponse(
                    {"ok": False, "error": str(exc)},
                    status_code=500,
                )

        @app.post(
            "/api/local/customise"
        )
        async def local_save_customise(
            request: Request,
        ):
            if not self._authorize_local(request):
                return JSONResponse(
                    {"ok": False, "error": "Local access required."},
                    status_code=403,
                )

            try:
                body = await request.json()
            except Exception:
                return JSONResponse(
                    {"ok": False, "error": "Invalid JSON body."},
                    status_code=400,
                )

            settings_file = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "settings"
                / "jarvis_settings.json"
            )

            try:
                settings_file.parent.mkdir(parents=True, exist_ok=True)
                settings = {}

                if settings_file.exists():
                    try:
                        with settings_file.open("r", encoding="utf-8") as f:
                            settings = json.load(f)
                    except Exception:
                        settings = {}

                if "assistantName" in body and body["assistantName"]:
                    settings["assistantName"] = str(body["assistantName"]).strip()
                if "userName" in body:
                    settings["userName"] = str(body["userName"]).strip()
                if "assistantColour" in body and body["assistantColour"]:
                    settings["assistantColour"] = str(body["assistantColour"]).strip()

                with settings_file.open("w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)
                    f.write("\n")

                print(
                    f"[LOCAL CUSTOMISE] Updated name: {settings.get('assistantName')} | colour: {settings.get('assistantColour')}"
                )

                return {"ok": True, "settings": settings}
            except Exception as exc:
                return JSONResponse(
                    {"ok": False, "error": str(exc)},
                    status_code=500,
                )

        # =====================================================
        # COMMAND
        # =====================================================

        @app.post(
            "/api/command"
        )
        async def command(
            request: Request,
        ):

            self._loop = (
                asyncio.get_running_loop()
            )

            if not (
                self._authorize(request)
                or self._authorize_local(request)
            ):
                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Unauthorized."
                        ),
                    },
                    status_code=401,
                )

            try:

                body = (
                    await request.json()
                )

            except Exception:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Invalid request."
                        ),
                    },
                    status_code=400,
                )

            token = (
                self._get_token(
                    request
                )
            )

            encrypted = str(
                body.get(
                    "enc",
                    "",
                )
            ).strip()

            if encrypted:

                if not token:

                    return JSONResponse(
                        {
                            "ok": False,
                            "error": (
                                "Unauthorized."
                            ),
                        },
                        status_code=401,
                    )

                session_key = (
                    self._token_keys.get(
                        token
                    )
                )

                if not session_key:

                    return JSONResponse(
                        {
                            "ok": False,
                            "error": (
                                "Session expired."
                            ),
                        },
                        status_code=401,
                    )

                try:

                    text = (
                        _decrypt_cbc(
                            _derive_key(
                                session_key
                            ),
                            encrypted,
                        )
                        .strip()
                    )

                except Exception:

                    return JSONResponse(
                        {
                            "ok": False,
                            "error": (
                                "Decryption failed."
                            ),
                        },
                        status_code=400,
                    )

            else:

                text = str(
                    body.get(
                        "text",
                        body.get("command", ""),
                    )
                ).strip()

            if not text:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Command is empty."
                        ),
                    },
                    status_code=400,
                )

            threading.Thread(
                target=self._run_command,
                args=(text,),
                daemon=True,
                name=(
                    "JARVIS-RemoteCommand"
                ),
            ).start()

            return {
                "ok": True,
                "message": (
                    "Command sent to JARVIS."
                ),
            }

        # =====================================================
        # WAKE
        # =====================================================

        @app.post(
            "/api/wake"
        )
        async def wake(
            request: Request,
        ):

            if not self._authorize(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Unauthorized."
                        ),
                    },
                    status_code=401,
                )

            threading.Thread(
                target=self._run_command,
                args=(
                    "hey jarvis",
                ),
                daemon=True,
                name=(
                    "JARVIS-RemoteWake"
                ),
            ).start()

            return {
                "ok": True
            }
            
        # =====================================================
        # DIRECT LIVE STATUS
        # =====================================================

        @app.get(
            "/api/live/status"
        )
        async def live_status(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Unauthorized."
                        ),
                    },
                    status_code=401,
                )

            try:

                from voice.live_conversation import (
                    live_conversation_status,
                )

                running = (
                    live_conversation_status()
                    == "Live conversation is running."
                )

                return {
                    "ok": True,
                    "running": running,
                }

            except Exception as exc:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(exc),
                    },
                    status_code=500,
                )

        # =====================================================
        # DIRECT LIVE START
        # =====================================================

        @app.post(
            "/api/live/start"
        )
        async def live_start(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Unauthorized."
                        ),
                    },
                    status_code=401,
                )

            try:

                from voice.live_conversation import (
                    start_live_conversation,
                )

                result = (
                    start_live_conversation()
                )

                await self.broadcast({
                    "type": "sys",
                    "text": (
                        "Live Conversation "
                        "start requested."
                    ),
                })

                return {
                    "ok": True,
                    "result": str(
                        result
                    ),
                }

            except Exception as exc:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(
                            exc
                        ),
                    },
                    status_code=500,
                )

        # =====================================================
        # DIRECT LIVE STOP
        # =====================================================

        @app.post(
            "/api/live/stop"
        )
        async def live_stop(
            request: Request,
        ):

            if not self._authorize_local(
                request
            ):

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Unauthorized."
                        ),
                    },
                    status_code=401,
                )

            if not self.live_stop_handler:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Live stop handler "
                            "is not connected."
                        ),
                    },
                    status_code=503,
                )

            try:

                result = (
                    self.live_stop_handler()
                )

                await self.broadcast({
                    "type": "sys",
                    "text": (
                        "Live Conversation "
                        "stop requested."
                    ),
                })

                return {
                    "ok": True,
                    "result": str(
                        result
                    ),
                }

            except Exception as exc:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": str(
                            exc
                        ),
                    },
                    status_code=500,
                )

        # =====================================================
        # FILE UPLOAD
        # =====================================================

        if (
            MULTIPART_AVAILABLE
            and UploadFile is not None
        ):

            @app.post(
                "/api/upload"
            )
            async def upload(
                request: Request,
                file: UploadFile = File(...),
            ):

                if not self._authorize(
                    request
                ):

                    return JSONResponse(
                        {
                            "ok": False,
                            "error": (
                                "Unauthorized."
                            ),
                        },
                        status_code=401,
                    )

                original_name = (
                    file.filename
                    or "upload"
                )

                safe_name = (
                    Path(
                        original_name
                    ).name
                )

                if not safe_name:

                    safe_name = "upload"

                target = (
                    self._unique_upload_path(
                        safe_name
                    )
                )

                total = 0

                limit = (
                    MAX_UPLOAD_MB
                    * 1024
                    * 1024
                )

                try:

                    with target.open(
                        "wb"
                    ) as output:

                        while True:

                            chunk = (
                                await file.read(
                                    1024 * 1024
                                )
                            )

                            if not chunk:

                                break

                            total += len(
                                chunk
                            )

                            if total > limit:

                                output.close()

                                target.unlink(
                                    missing_ok=True
                                )

                                return JSONResponse(
                                    {
                                        "ok": False,
                                        "error": (
                                            "File exceeds "
                                            f"{MAX_UPLOAD_MB} MB."
                                        ),
                                    },
                                    status_code=413,
                                )

                            output.write(
                                chunk
                            )

                finally:

                    await file.close()

                print(
                    "[REMOTE] File received:",
                    target,
                )

                await self.broadcast({
                    "type": "file_received",
                    "name": target.name,
                    "size": total,
                })

                return {
                    "ok": True,
                    "name": target.name,
                    "size": total,
                }

        # =====================================================
        # FILE DOWNLOAD
        # =====================================================

        @app.get(
            "/uploads/{filename}"
        )
        async def download(
            filename: str,
            token: str = "",
        ):

            if token not in self._tokens:

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "Unauthorized."
                        ),
                    },
                    status_code=401,
                )

            safe_name = (
                Path(
                    filename
                ).name
            )

            path = (
                UPLOADS_DIR
                / safe_name
            )

            if not path.is_file():

                return JSONResponse(
                    {
                        "ok": False,
                        "error": (
                            "File not found."
                        ),
                    },
                    status_code=404,
                )

            return FileResponse(
                str(path),
                filename=safe_name,
            )

        # =====================================================
        # DASHBOARD WEBSOCKET
        # =====================================================

        @app.websocket(
            "/ws"
        )
        async def websocket(
            websocket: WebSocket,
            token: str = "",
        ):

            self._loop = (
                asyncio.get_running_loop()
            )

            if token not in self._tokens:

                await websocket.close(
                    code=4001
                )

                return

            await websocket.accept()

            self._clients.add(
                websocket
            )

            try:

                for message in (
                    self._history[-100:]
                ):

                    await websocket.send_json(
                        message
                    )

                await websocket.send_json({
                    "type": "status",
                    "state": "active",
                })

                await websocket.send_json({
                    "type": "sys",
                    "text": (
                        "Remote session active."
                    ),
                })

                while True:

                    await websocket.receive_text()

            except WebSocketDisconnect:

                pass

            except Exception as exc:

                print(
                    "[REMOTE WS ERROR]",
                    exc,
                )

            finally:

                self._clients.discard(
                    websocket
                )

        # =====================================================
        # PHONE AUDIO
        # =====================================================

        @app.websocket(
            "/ws/phone-audio"
        )
        async def phone_audio(
            websocket: WebSocket,
            token: str = "",
        ):

            self._loop = (
                asyncio.get_running_loop()
            )

            if token not in self._tokens:

                await websocket.close(
                    code=4001
                )

                return

            await websocket.accept()

            await self.broadcast({
                "type": "sys",
                "text": (
                    "Phone microphone live."
                ),
            })

            try:

                while True:

                    data = (
                        await websocket.receive_bytes()
                    )

                    try:

                        self._phone_audio_queue.put_nowait(
                            data
                        )

                    except asyncio.QueueFull:

                        try:

                            self._phone_audio_queue.get_nowait()

                        except asyncio.QueueEmpty:

                            pass

                        try:

                            self._phone_audio_queue.put_nowait(
                                data
                            )

                        except asyncio.QueueFull:

                            pass

            except WebSocketDisconnect:

                pass

            finally:

                await self.broadcast({
                    "type": "sys",
                    "text": (
                        "Phone microphone stopped."
                    ),
                })

        return app

    # =========================================================
    # UNIQUE UPLOAD PATH
    # =========================================================

    @staticmethod
    def _unique_upload_path(
        filename: str,
    ) -> Path:

        base = Path(
            filename
        )

        stem = base.stem

        suffix = base.suffix

        candidate = (
            UPLOADS_DIR
            / filename
        )

        counter = 1

        while candidate.exists():

            candidate = (
                UPLOADS_DIR
                / (
                    f"{stem}_"
                    f"{counter}"
                    f"{suffix}"
                )
            )

            counter += 1

        return candidate

    # =========================================================
    # PHONE AUDIO QUEUE
    # =========================================================

    def phone_audio_queue(self):

        return (
            self._phone_audio_queue
        )

    # =========================================================
    # START
    # =========================================================

    def start(self) -> bool:

        if not FASTAPI_AVAILABLE:

            print(
                "[REMOTE] Disabled."
            )

            print(
                "[REMOTE] Install:"
            )

            print(
                "pip install fastapi "
                '"uvicorn[standard]" '
                "cryptography"
            )

            return False

        if (
            self._thread
            and self._thread.is_alive()
        ):

            return True

        def run_server():

            try:

                uvicorn.run(
                    self.app,
                    host="0.0.0.0",
                    port=self.port,
                    log_level="warning",
                )

            except Exception as exc:

                print(
                    "[REMOTE] Server stopped:",
                    exc,
                )

        self._thread = (
            threading.Thread(
                target=run_server,
                daemon=True,
                name=(
                    "JARVIS-DashboardServer"
                ),
            )
        )

        self._thread.start()

        print(
            "[REMOTE] Dashboard Server:"
        )

        print(
            f"[REMOTE] {self.url()}"
        )

        return True

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        self._tokens.clear()

        self._token_keys.clear()

        self._device_sessions.clear()

        self._pin = None

        self._pin_expiry = 0.0