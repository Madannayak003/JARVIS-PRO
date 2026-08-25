"""
Background Services
"""

from services.remote_control import RemoteControlServer

SERVICES = {


}


def start_all():

    print("[SERVICES] Ready")
    
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