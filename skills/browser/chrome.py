import os
import subprocess
import psutil
import time
import requests


class ChromeController:

    def __init__(self):

        self.chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    def running(self):

        for p in psutil.process_iter(["name"]):

            try:
                if p.info["name"] and "chrome.exe" == p.info["name"].lower():
                    return True
            except:
                pass

        return False

    def start(self):

        # Is CDP already available?
        try:
            requests.get("http://127.0.0.1:9223/json", timeout=1)
            return
        except:
            pass

        profile = os.path.join(
            os.environ["TEMP"],
            "JarvisChrome"
        )

        subprocess.Popen([
            self.chrome,
            f"--user-data-dir={profile}",
            "--remote-debugging-port=9223",
            "--new-window",
            "about:blank"
        ])

        # Wait until Chrome actually starts
        for _ in range(40):

            try:

                requests.get(
                    "http://127.0.0.1:9223/json",
                    timeout=0.5
                )

                print("[CHROME] Debug Ready")

                return

            except:

                time.sleep(0.25)

        raise RuntimeError("Chrome debugging failed to start")


chrome = ChromeController()