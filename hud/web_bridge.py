"""
JARVIS PRO
HUD Web Bridge

UI-1.5: Python -> Web HUD event bridge.

This module is passive: it only forwards HUDState/HUDEvent
information to the browser. It does not execute JARVIS commands.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Empty, Queue
from typing import Any

from .bus import hud_bus
from .manager import hud


class _Client:
    def __init__(self) -> None:
        self.queue: Queue[str] = Queue()
        self.alive = True


class _BridgeHandler(BaseHTTPRequestHandler):
    bridge: "HUDWebBridge"

    server_version = "JARVIS-HUD/1.5"

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")

    def _json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json({"ok": True, "service": "jarvis-hud-bridge", "version": "1.5"})
            return

        if self.path == "/state":
            self._json(self.bridge.state_payload())
            return

        if self.path == "/events":
            self._events()
            return

        self._json({"error": "Not found"}, 404)
        
    def do_POST(self) -> None:

        if self.path == "/shutdown":

            self.bridge.request_shutdown()

            self._json({
                "ok": True,
                "message": "JARVIS shutdown requested.",
            })

            return

        self._json(
            {"error": "Not found"},
            404,
        )

    def _events(self) -> None:
        client = self.bridge.add_client()

        try:
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            # Always send a current snapshot immediately.
            initial = self.bridge.state_payload()
            self.wfile.write(
                f"event: state\ndata: {json.dumps(initial, ensure_ascii=False)}\n\n".encode()
            )
            self.wfile.flush()

            while client.alive:
                try:
                    message = client.queue.get(timeout=15)
                    self.wfile.write(message.encode("utf-8"))
                    self.wfile.flush()
                except Empty:
                    # Keep the SSE connection alive through idle periods.
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()

        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            client.alive = False
            self.bridge.remove_client(client)

    def log_message(self, format: str, *args: Any) -> None:
        # Keep the JARVIS console clean.
        return


class HUDWebBridge:
    """
    Small local SSE server that mirrors the existing HUD event bus.

    Default:
        http://127.0.0.1:8766
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8766) -> None:
        self.host = host
        self.port = port
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._clients: list[_Client] = []
        self._lock = threading.Lock()
        self._subscribed = False
        self._shutdown_callback = None

    def start(self) -> bool:
        if self._server is not None:
            return True

        try:
            handler = type(
                "HUDWebBridgeHandler",
                (_BridgeHandler,),
                {"bridge": self},
            )
            self._server = ThreadingHTTPServer((self.host, self.port), handler)
            self._subscribe()

            self._thread = threading.Thread(
                target=self._server.serve_forever,
                name="jarvis-hud-web-bridge",
                daemon=True,
            )
            self._thread.start()

            print(
                f"[HUD WEB] Bridge started: "
                f"http://{self.host}:{self.port}"
            )
            return True

        except OSError as exc:
            print(f"[HUD WEB] Bridge failed to start: {exc}")
            self._server = None
            return False

    def stop(self) -> None:
        if self._server is None:
            return

        self._unsubscribe()

        server = self._server
        self._server = None
        server.shutdown()
        server.server_close()

        with self._lock:
            clients = list(self._clients)
            self._clients.clear()

        for client in clients:
            client.alive = False

        print("[HUD WEB] Bridge stopped.")
        
    def set_shutdown_callback(
        self,
        callback,
    ) -> None:

        self._shutdown_callback = callback


    def request_shutdown(self) -> None:

        print(
            "[HUD WEB] Shutdown requested by desktop HUD."
        )

        callback = self._shutdown_callback

        if callback is None:

            print(
                "[HUD WEB] No shutdown callback registered."
            )

            return

        threading.Thread(
            target=callback,
            name="jarvis-shutdown-request",
            daemon=True,
        ).start()

    def _subscribe(self) -> None:
        if self._subscribed:
            return
        hud_bus.subscribe(self._on_event)
        self._subscribed = True

    def _unsubscribe(self) -> None:
        if not self._subscribed:
            return
        hud_bus.unsubscribe(self._on_event)
        self._subscribed = False

    def add_client(self) -> _Client:
        client = _Client()
        with self._lock:
            self._clients.append(client)
        return client

    def remove_client(self, client: _Client) -> None:
        with self._lock:
            if client in self._clients:
                self._clients.remove(client)

    def _on_event(self, event: Any) -> None:
        payload = {
            "name": getattr(event, "name", ""),
            "data": getattr(event, "data", {}) or {},
            "timestamp": getattr(event, "timestamp", ""),
            "source": getattr(event, "source", None),
            "state": self.state_payload(),
        }

        message = (
            "event: hud\n"
            f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        )

        with self._lock:
            clients = list(self._clients)

        for client in clients:
            if not client.alive:
                continue
            try:
                client.queue.put_nowait(message)
            except Exception:
                client.alive = False

    def state_payload(self) -> dict[str, Any]:
        state = hud.state

        return {
            "status": state.status,
            "voice_mode": state.voice_mode,
            "ai_model": state.ai_model,
            "current_task": state.current_task,
            "task_status": state.task_status,
            "listening": state.listening,
            "speaking": state.speaking,
            "thinking": state.thinking,
            "executing": state.executing,
            "system": dict(state.system),
            "notification": state.notification,
            "error": state.error,
            "last_event": state.last_event,
            "last_update": state.last_update,
        }


# Global bridge instance.
hud_web = HUDWebBridge()
