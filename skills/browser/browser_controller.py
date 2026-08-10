from playwright.sync_api import sync_playwright
import webbrowser
import pygetwindow as gw

import threading

import os
import time
import requests
import subprocess

class BrowserController:

    def __init__(self):

        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):

        print(
            f"[Browser THREAD] "
            f"{threading.current_thread().name} | "
            f"ID: {threading.get_ident()}"
        )

        # -------------------------------------------------
        # Already connected
        # -------------------------------------------------

        try:

            if (
                self.browser
                and self.browser.is_connected()
                and self.page
                and not self.page.is_closed()
            ):

                return

        except:

            pass

        # -------------------------------------------------
        # Start Playwright
        # -------------------------------------------------

        if not self.playwright:

            self.playwright = sync_playwright().start()

        # -------------------------------------------------
        # Check existing JARVIS Chrome
        # -------------------------------------------------

        try:

            requests.get(
                "http://127.0.0.1:9223/json/version",
                timeout=1
            )

            chrome_running = True

        except:

            chrome_running = False

        # -------------------------------------------------
        # Start JARVIS Chrome automatically
        # -------------------------------------------------

        if not chrome_running:

            chrome_path = (
                r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            )

            profile_path = os.path.join(
                os.environ["LOCALAPPDATA"],
                "JARVIS",
                "ChromeProfile"
            )

            os.makedirs(profile_path, exist_ok=True)

            print("[Browser] Starting JARVIS Chrome...")

            subprocess.Popen(
                [
                    chrome_path,
                    "--remote-debugging-port=9223",
                    f"--user-data-dir={profile_path}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait for Chrome debugging
            for _ in range(20):

                try:

                    requests.get(
                        "http://127.0.0.1:9223/json/version",
                        timeout=1
                    )

                    break

                except:

                    time.sleep(0.5)

            else:

                print("[Browser ERROR] Chrome debugging did not start")

                return

        # -------------------------------------------------
        # Connect through CDP
        # -------------------------------------------------

        try:

            self.browser = self.playwright.chromium.connect_over_cdp(
                "http://127.0.0.1:9223"
            )

            print("[Browser] Connected to JARVIS Chrome")

            # -------------------------------------------------
            # Find YouTube tab
            # -------------------------------------------------

            for context in self.browser.contexts:

                for page in context.pages:

                    if "youtube.com" in page.url:

                        self.page = page

                        print("[Browser] YouTube tab attached")

                        return

            # -------------------------------------------------
            # No YouTube tab yet
            # -------------------------------------------------

            context = self.browser.contexts[0]

            self.page = context.pages[0]

            print("[Browser] Chrome attached")

        except Exception as e:

            print(f"[Browser ERROR] CDP connection failed: {e}")

            self.browser = None
            self.page = None
        
        
    def open(self, url):

        self.start()

        try:

            self.page.goto(url)

        except:

            print("[Browser] Reopening...")

            self.browser = None
            self.page = None

            self.start()

            self.page.goto(url)
        

    def search_google(self, query):

        self.start()

        try:

            self.page.goto(
                f"https://www.google.com/search?q={query}"
            )

        except:

            self.browser = None
            self.page = None

            self.start()

            self.page.goto(
                f"https://www.google.com/search?q={query}"
            )
        
        
    def search_youtube(self, query):

        self.start()

        try:

            self.page.goto(
                f"https://www.youtube.com/results?search_query={query}"
            )

        except:

            self.browser = None
            self.page = None

            self.start()

            self.page.goto(
                f"https://www.youtube.com/results?search_query={query}"
            )
        

    def play_video(self, video_id):

        if not video_id:
            return False

        url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"[YouTube] Opening in JARVIS Chrome: {url}")

        try:

            self.start()

            # Use the JARVIS Chrome CDP context
            context = self.browser.contexts[0]

            # Look for existing YouTube page
            youtube_page = None

            for page in context.pages:

                if "youtube.com" in page.url:
                    youtube_page = page
                    break

            # If no YouTube tab exists, create one
            if not youtube_page:
                youtube_page = context.new_page()

            self.page = youtube_page

            # Open video directly in JARVIS Chrome
            self.page.goto(url)

            self.page.bring_to_front()

            print("[YouTube] Video opened in JARVIS Chrome")

            # Give YouTube a moment to load an advertisement
            
            # Skip ad if the Skip button is available
            self.skip_ad()

            return True

        except Exception as e:

            print(f"[YouTube ERROR] {e}")

            return False
        
    def play_first_video(self):
        try:
            self.start()

            if not self.browser or not self.page:
                print("[YouTube] Browser not connected")
                return False

            # Make sure we are on a YouTube page
            if "youtube.com" not in self.page.url:
                print("[YouTube] Current page is not YouTube")
                return False

            # Click the first video result
            first_video = self.page.locator(
                "ytd-video-renderer a#video-title"
            ).first

            if not first_video.is_visible():
                print("[YouTube] First video not found")
                return False

            first_video.click()

            self.page.bring_to_front()

            print("[YouTube] First video opened in JARVIS Chrome")

            return True

        except Exception as e:
            print(f"[YouTube ERROR] First video failed: {e}")
            return False
        
    def skip_ad(self):

        self.start()

        if not self.page:
            return False

        try:

            # Wait up to 15 seconds for YouTube's Skip button
            for _ in range(30):

                button = self.page.get_by_text("Skip", exact=True)

                if button.count() > 0:

                    button.first.click()

                    print("[YouTube] Ad skipped")

                    return True

                time.sleep(0.5)

        except Exception as e:

            print(f"[YouTube] Skip ad failed: {e}")

        print("[YouTube] No skippable ad found")

        return False

    def youtube_key(self, key):

        try:

            # Reconnect to JARVIS Chrome
            self.start()

            if not self.browser:
                print("[YouTube] Browser not connected")
                return False

            # Find the actual YouTube page
            youtube_page = None

            for context in self.browser.contexts:

                for page in context.pages:

                    if "youtube.com/watch" in page.url:

                        youtube_page = page
                        break

                if youtube_page:
                    break

            if not youtube_page:
                print("[YouTube] YouTube video page not found")
                return False

            self.page = youtube_page

            # Send key DIRECTLY to YouTube page
            self.page.bring_to_front()

            self.page.keyboard.press(key)

            print(f"[YouTube] Key sent to YouTube page: {key}")

            return True

        except Exception as e:

            print(f"[YouTube CONTROL ERROR] {e}")

            return False


    def pause_video(self):

        return self.youtube_key("k")


    def resume_video(self):

        return self.youtube_key("k")


    def fullscreen(self):

        return self.youtube_key("f")


    def next_video(self):

        try:

            self.start()

            if not self.browser:
                print("[YouTube] Browser not connected")
                return False

            youtube_page = None

            for context in self.browser.contexts:

                for page in context.pages:

                    if "youtube.com/watch" in page.url:

                        youtube_page = page
                        break

                if youtube_page:
                    break

            if not youtube_page:
                print("[YouTube] YouTube video page not found")
                return False

            self.page = youtube_page

            self.page.keyboard.press("Shift+n")

            print("[YouTube] Next video command sent")

            return True

        except Exception as e:

            print(f"[YouTube NEXT ERROR] {e}")

            return False


    def previous_video(self):

        try:

            self.start()

            if not self.browser:
                print("[YouTube] Browser not connected")
                return False

            youtube_page = None

            for context in self.browser.contexts:

                for page in context.pages:

                    if "youtube.com/watch" in page.url:

                        youtube_page = page
                        break

                if youtube_page:
                    break

            if not youtube_page:
                print("[YouTube] YouTube video page not found")
                return False

            self.page = youtube_page

            self.page.keyboard.press("Shift+P")

            print("[YouTube] Previous video command sent")

            return True

        except Exception as e:

            print(f"[YouTube PREVIOUS ERROR] {e}")

            return False

    def new_tab(self):

        self.page = self.browser.new_page()

    def close_tab(self):

        self.page.close()

    def refresh(self):

        self.page.reload()

    def back(self):

        self.page.go_back()

    def forward(self):

        self.page.go_forward()

    def scroll_down(self):

        self.page.mouse.wheel(0, 1000)

    def scroll_up(self):

        self.page.mouse.wheel(0, -1000)
        
    def close(self):

        try:

            if self.page:
                self.page.close()
        except:
            pass

        try:

            if self.browser:
                self.browser.close()
        except:
            pass

        try:

            if self.playwright:
                self.playwright.stop()
        except:
            pass

        self.page = None
        self.browser = None
        self.playwright = None        


browser = BrowserController()