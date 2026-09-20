"""Safe subprocess transport for Android Debug Bridge."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

from .models import AdbCommandResult, AndroidDevice


DEFAULT_ADB_PATH = Path(r"C:\platform-tools\adb.exe")
_NO_DEVICE_COMMANDS = {"version", "devices", "start-server", "kill-server"}


class AdbError(RuntimeError):
    """Base error for an unavailable or failed ADB operation."""


class AdbNotFoundError(AdbError):
    """Raised when no usable ADB executable can be found."""


class AdbDeviceError(AdbError):
    """Raised when a device operation needs a connected device."""


class AdbCommandError(AdbError):
    """Raised when a checked ADB command returns a failure."""

    def __init__(self, result: AdbCommandResult):
        detail = result.stderr.strip() or result.stdout.strip()
        super().__init__(detail or f"ADB exited with code {result.returncode}.")
        self.result = result


class AdbClient:
    """Run ADB using safe subprocess argument lists and no shell."""

    def __init__(
        self,
        adb_path: str | os.PathLike[str] | None = None,
        device_id: str | None = None,
        timeout: float = 15.0,
        runner=subprocess.run,
    ):
        self._explicit_adb_path = str(adb_path) if adb_path else None
        self.device_id = device_id or os.getenv("ANDROID_DEVICE_ID", "").strip()
        self.timeout = timeout
        self._runner = runner
        self._selected_device_id: str | None = None

    @property
    def adb_path(self) -> str | None:
        """Resolve configured ADB, PATH ADB, then the existing Windows fallback."""
        configured = self._explicit_adb_path or os.getenv("ANDROID_ADB_PATH", "").strip()
        if configured:
            return configured
        path_adb = shutil.which("adb")
        if path_adb:
            return path_adb
        if DEFAULT_ADB_PATH.exists():
            return str(DEFAULT_ADB_PATH)
        return None

    @property
    def selected_device_id(self) -> str | None:
        return self._selected_device_id or self.device_id or None

    def _require_adb(self) -> str:
        path = self.adb_path
        if not path:
            raise AdbNotFoundError(
                "ADB was not found. Set ANDROID_ADB_PATH or install platform-tools."
            )
        return path

    def run_adb(
        self,
        args: Sequence[str],
        *,
        device: str | None = None,
        timeout: float | None = None,
        check: bool = False,
    ) -> AdbCommandResult:
        """Run one ADB command with each argument passed separately."""
        if not args:
            raise ValueError("ADB arguments cannot be empty.")

        normalized_args = [str(value) for value in args]
        path = self._require_adb()
        command = [path]
        if normalized_args[0] not in _NO_DEVICE_COMMANDS:
            requested_device = device or self.selected_device_id
            if requested_device:
                command.extend(["-s", requested_device])
            else:
                selected = self.select_device()
                if not selected:
                    raise AdbDeviceError("No online Android device is connected.")
                command.extend(["-s", selected.serial])
        command.extend(normalized_args)

        try:
            completed = self._runner(
                command,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
                check=False,
                shell=False,
            )
        except FileNotFoundError as error:
            raise AdbNotFoundError(f"ADB executable is not available: {path}") from error
        except subprocess.TimeoutExpired as error:
            raise AdbError("ADB command timed out.") from error
        except OSError as error:
            raise AdbError(f"ADB could not be started: {error}") from error

        result = AdbCommandResult(
            command=tuple(command),
            returncode=int(completed.returncode),
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
        )
        if check and not result.ok:
            raise AdbCommandError(result)
        return result

    def is_available(self) -> bool:
        try:
            return self.run_adb(["version"]).ok
        except AdbError:
            return False

    def detect_adb(self) -> bool:
        """Compatibility-friendly name for the ADB availability check."""
        return self.is_available()

    def get_devices(self) -> list[AndroidDevice]:
        result = self.run_adb(["devices", "-l"])
        if not result.ok:
            return []

        devices: list[AndroidDevice] = []
        for raw_line in result.stdout.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("List of devices"):
                continue
            fields = line.split()
            if len(fields) < 2:
                continue
            attributes: dict[str, str] = {}
            for field in fields[2:]:
                if ":" in field:
                    key, value = field.split(":", 1)
                    attributes[key] = value
            devices.append(
                AndroidDevice(
                    serial=fields[0],
                    state=fields[1],
                    product=attributes.get("product", ""),
                    model=attributes.get("model", "").replace("_", " "),
                    device=attributes.get("device", ""),
                    transport_id=attributes.get("transport_id", ""),
                )
            )
        return devices

    def select_device(self, device_id: str | None = None) -> AndroidDevice | None:
        devices = self.get_devices()
        requested = device_id or self.device_id
        if requested:
            selected = next(
                (item for item in devices if item.serial == requested and item.is_online),
                None,
            )
        else:
            selected = next((item for item in devices if item.is_online), None)
        self._selected_device_id = selected.serial if selected else None
        return selected

    def shell(
        self,
        args: Sequence[str],
        *,
        device: str | None = None,
        check: bool = False,
    ) -> AdbCommandResult:
        """Run ``adb shell`` with safe individual arguments."""
        return self.run_adb(
            ["shell", *[str(value) for value in args]],
            device=device,
            check=check,
        )
