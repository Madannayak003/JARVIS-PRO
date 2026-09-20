"""
Background Services
"""

from services.remote_control import RemoteControlServer

SERVICES = {


}

_phone_call_monitor = None


def start_all():

    print("[SERVICES] Ready")

    global _phone_call_monitor
    try:
        from skills.phone_call.monitor import start_phone_call_monitor

        _phone_call_monitor = start_phone_call_monitor()
        print("[SERVICES] Phone Call monitor started.")
    except Exception as error:
        print(f"[SERVICES] Phone Call monitor unavailable: {error}")


def stop_all():
    global _phone_call_monitor
    if _phone_call_monitor is None:
        return
    try:
        from skills.phone_call.monitor import stop_phone_call_monitor

        stop_phone_call_monitor()
        print("[SERVICES] Phone Call monitor stopped.")
    except Exception as error:
        print(f"[SERVICES] Phone Call monitor shutdown skipped: {error}")
    finally:
        _phone_call_monitor = None
    
remote_server = None

def start_remote_control(command_handler):
    global remote_server

    remote_server = RemoteControlServer(
        command_handler=command_handler
    )

    if remote_server.start():
        print(
            "[REMOTE] Open:",
            remote_server.url()
        )

    return remote_server
