from playwright.sync_api import sync_playwright
import threading
import os
import time
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor


# =========================================================
# GLOBAL BROWSER LOCK
# =========================================================

_browser_lock = threading.RLock()


# =========================================================
# BROWSER WORKER
# =========================================================
#
# IMPORTANT:
#
# Playwright Sync API must NOT execute inside Gemini Live's
# asyncio event loop.
#
# All browser operations are therefore routed through ONE
# dedicated worker thread.
#
# This worker permanently owns:
#
#     Playwright
#     Browser
#     Page
#
# This also keeps Playwright objects on the same thread.
# =========================================================

class BrowserWorker:

    def __init__(self):

        self.executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="JARVIS-BrowserWorker",
        )

        self.worker_thread_id = None

    def run(self, function, *args, **kwargs):

        # -------------------------------------------------
        # Already inside browser worker
        # -------------------------------------------------

        if (
            self.worker_thread_id
            == threading.get_ident()
        ):

            return function(
                *args,
                **kwargs,
            )

        # -------------------------------------------------
        # Send operation to dedicated browser thread
        # -------------------------------------------------

        future = self.executor.submit(
            self._execute,
            function,
            args,
            kwargs,
        )

        return future.result()

    def _execute(
        self,
        function,
        args,
        kwargs,
    ):

        self.worker_thread_id = threading.get_ident()

        return function(
            *args,
            **kwargs,
        )

    def shutdown(self):

        try:

            self.executor.shutdown(
                wait=False,
                cancel_futures=True,
            )

        except Exception:

            pass


_browser_worker = BrowserWorker()


# =========================================================
# BROWSER CONTROLLER
# =========================================================

class BrowserController:

    def __init__(self):

        # -------------------------------------------------
        # Playwright state belongs to browser worker thread
        # -------------------------------------------------

        self.playwright = None
        self.browser = None
        self.page = None
        
        # -------------------------------------------------
        # Previous browser page
        # -------------------------------------------------
        #
        # Used when JARVIS opens a new tab and the user says
        # "go back". A newly-created tab has no history, so
        # JARVIS should return to the previous tab.
        #
        self.previous_page = None

    # =====================================================
    # INTERNAL EXECUTION
    # =====================================================

    def _run_browser(
        self,
        function,
        *args,
        **kwargs,
    ):

        return _browser_worker.run(
            function,
            *args,
            **kwargs,
        )

    # =====================================================
    # START
    # =====================================================

    def start(self):

        return self._run_browser(
            self._start_impl
        )

    def _start_impl(self):

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

                return True

        except Exception:

            pass

        # -------------------------------------------------
        # Start Playwright
        # -------------------------------------------------

        if not self.playwright:

            print(
                "[Browser] Starting Playwright..."
            )

            self.playwright = (
                sync_playwright().start()
            )

        # -------------------------------------------------
        # Check existing JARVIS Chrome
        # -------------------------------------------------

        try:

            requests.get(
                "http://127.0.0.1:9223/json/version",
                timeout=1,
            )

            chrome_running = True

        except Exception:

            chrome_running = False

        # -------------------------------------------------
        # Start JARVIS Chrome automatically
        # -------------------------------------------------

        if not chrome_running:

            chrome_path = (
                r"C:\Program Files\Google\Chrome"
                r"\Application\chrome.exe"
            )

            profile_path = os.path.join(
                os.environ["LOCALAPPDATA"],
                "JARVIS",
                "ChromeProfile",
            )

            os.makedirs(
                profile_path,
                exist_ok=True,
            )

            print(
                "[Browser] Starting JARVIS Chrome..."
            )

            try:

                subprocess.Popen(
                    [
                        chrome_path,
                        "--remote-debugging-port=9223",
                        f"--user-data-dir={profile_path}",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            except Exception as e:

                print(
                    "[Browser ERROR] "
                    f"Could not start Chrome: {e}"
                )

                return False

            # -------------------------------------------------
            # Wait for Chrome debugging
            # -------------------------------------------------

            for _ in range(20):

                try:

                    requests.get(
                        "http://127.0.0.1:9223/json/version",
                        timeout=1,
                    )

                    chrome_running = True

                    break

                except Exception:

                    time.sleep(0.5)

            if not chrome_running:

                print(
                    "[Browser ERROR] "
                    "Chrome debugging did not start"
                )

                return False

        # -------------------------------------------------
        # Connect through CDP
        # -------------------------------------------------

        try:

            self.browser = (
                self.playwright
                .chromium
                .connect_over_cdp(
                    "http://127.0.0.1:9223"
                )
            )

            print(
                "[Browser] Connected to JARVIS Chrome"
            )

            # -------------------------------------------------
            # Find existing YouTube tab
            # -------------------------------------------------

            for context in self.browser.contexts:

                for page in context.pages:

                    try:

                        if "youtube.com" in page.url:

                            self.page = page

                            print(
                                "[Browser] "
                                "YouTube tab attached"
                            )

                            return True

                    except Exception:

                        continue

            # -------------------------------------------------
            # Use first available page
            # -------------------------------------------------

            if not self.browser.contexts:

                print(
                    "[Browser ERROR] "
                    "No browser context available"
                )

                return False

            context = self.browser.contexts[0]

            if context.pages:

                self.page = context.pages[0]

            else:

                self.page = context.new_page()

            print(
                "[Browser] Chrome attached"
            )

            return True

        except Exception as e:

            print(
                "[Browser ERROR] "
                f"CDP connection failed: {e}"
            )

            self.browser = None
            self.page = None

            return False

    # =====================================================
    # OPEN
    # =====================================================

    def open(self, url):

        return self._run_browser(
            self._open_impl,
            url,
        )

    def _open_impl(self, url):

        if not url:

            return False

        print(
            f"[Browser OPEN THREAD] "
            f"{threading.current_thread().name} | "
            f"{threading.get_ident()}"
        )

        with _browser_lock:

            try:

                if not self._start_impl():

                    print(
                        "[Browser] "
                        "Browser could not start"
                    )

                    return False

                if not self.browser or not self.page:

                    print(
                        "[Browser] "
                        "Browser not connected"
                    )

                    return False

                print(
                    f"[Browser] Opening: {url}"
                )

                self.page.goto(
                    str(url),
                    wait_until="domcontentloaded",
                    timeout=15000,
                )

                self.page.bring_to_front()

                print(
                    "[Browser] "
                    "Page opened in JARVIS Chrome"
                )

                return True

            except Exception as e:

                print(
                    "[Browser ERROR] "
                    f"Open failed: {e}"
                )

                return False

    # =====================================================
    # GOOGLE SEARCH
    # =====================================================

    def search_google(self, query):

        return self._run_browser(
            self._search_google_impl,
            query,
        )

    def _search_google_impl(self, query):

        print(
            f"[Browser GOOGLE THREAD] "
            f"{threading.current_thread().name} | "
            f"{threading.get_ident()}"
        )

        if not query:

            return False

        with _browser_lock:

            try:

                import urllib.parse

                encoded_query = (
                    urllib.parse.quote(
                        str(query)
                    )
                )

                if not self._start_impl():

                    print(
                        "[Google] "
                        "Browser not connected"
                    )

                    return False

                if not self.browser or not self.page:

                    return False

                url = (
                    "https://www.google.com/search?q="
                    + encoded_query
                )

                print(
                    f"[Google] Searching: {query}"
                )

                self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=15000,
                )

                self.page.bring_to_front()

                print(
                    "[Google] "
                    "Search opened in JARVIS Chrome"
                )

                return True

            except Exception as e:

                print(
                    "[Google ERROR] "
                    f"Search failed: {e}"
                )

                return False

    # =====================================================
    # YOUTUBE SEARCH
    # =====================================================

    def search_youtube(self, query):

        return self._run_browser(
            self._search_youtube_impl,
            query,
        )

    def _search_youtube_impl(self, query):

        print(
            f"[Browser SEARCH THREAD] "
            f"{threading.current_thread().name} | "
            f"{threading.get_ident()}"
        )

        if not query:

            return False

        with _browser_lock:

            try:

                if not self._start_impl():

                    print(
                        "[YouTube] "
                        "Browser not connected"
                    )

                    return False

                if not self.browser or not self.page:

                    print(
                        "[YouTube] "
                        "Browser not connected"
                    )

                    return False

                import urllib.parse

                encoded_query = (
                    urllib.parse.quote(
                        str(query)
                    )
                )

                url = (
                    "https://www.youtube.com/results"
                    "?search_query="
                    + encoded_query
                )

                print(
                    f"[YouTube] Searching: {query}"
                )

                self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=15000,
                )

                self.page.bring_to_front()

                print(
                    "[YouTube] "
                    "Search opened in JARVIS Chrome"
                )

                return True

            except Exception as e:

                print(
                    "[YouTube ERROR] "
                    f"Search failed: {e}"
                )

                return False

    # =====================================================
    # GITHUB SEARCH
    # =====================================================

    def search_github(self, query):

        return self._run_browser(
            self._search_github_impl,
            query,
        )

    def _search_github_impl(self, query):

        print(
            f"[Browser GITHUB THREAD] "
            f"{threading.current_thread().name} | "
            f"{threading.get_ident()}"
        )

        if not query:

            return False

        try:

            if not self._start_impl():

                return False

            if not self.browser or not self.page:

                return False

            import urllib.parse

            url = (
                "https://github.com/search?q="
                + urllib.parse.quote(
                    str(query)
                )
            )

            print(
                f"[GitHub] Searching: {query}"
            )

            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=15000,
            )

            self.page.bring_to_front()

            print(
                "[GitHub] "
                "Search opened in JARVIS Chrome"
            )

            return True

        except Exception as e:

            print(
                f"[GitHub ERROR] {e}"
            )

            return False

    # =====================================================
    # PLAY VIDEO
    # =====================================================

    def play_video(self, video_id):

        return self._run_browser(
            self._play_video_impl,
            video_id,
        )

    def _play_video_impl(self, video_id):

        if not video_id:

            return False

        with _browser_lock:

            return self._play_video_locked(
                video_id
            )

    def _play_video_locked(self, video_id):

        print(
            f"[Browser PLAY THREAD] "
            f"{threading.current_thread().name} | "
            f"{threading.get_ident()}"
        )

        url = (
            "https://www.youtube.com/watch?v="
            f"{video_id}"
        )

        print(
            "[YouTube] "
            f"Opening in JARVIS Chrome: {url}"
        )

        try:

            if not self._start_impl():

                return False

            if not self.browser:

                return False

            context = (
                self.browser.contexts[0]
            )

            youtube_page = None

            for page in context.pages:

                try:

                    if "youtube.com" in page.url:

                        youtube_page = page

                        break

                except Exception:

                    continue

            if not youtube_page:

                youtube_page = (
                    context.new_page()
                )

            self.page = youtube_page

            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=15000,
            )

            self.page.bring_to_front()

            print(
                "[YouTube] "
                "Video opened in JARVIS Chrome"
            )

            self._skip_ad_impl()

            return True

        except Exception as e:

            print(
                f"[YouTube ERROR] {e}"
            )

            return False

    # =====================================================
    # PLAY FIRST VIDEO
    # =====================================================

    def play_first_video(self):

        return self._run_browser(
            self._play_first_video_impl
        )

    def _play_first_video_impl(self):

        try:

            if not self._start_impl():

                return False

            if not self.browser or not self.page:

                print(
                    "[YouTube] "
                    "Browser not connected"
                )

                return False

            if "youtube.com" not in self.page.url:

                print(
                    "[YouTube] "
                    "Current page is not YouTube"
                )

                return False

            first_video = (
                self.page
                .locator(
                    "ytd-video-renderer "
                    "a#video-title"
                )
                .first
            )

            if not first_video.is_visible():

                print(
                    "[YouTube] "
                    "First video not found"
                )

                return False

            first_video.click()

            self.page.bring_to_front()

            print(
                "[YouTube] "
                "First video opened in JARVIS Chrome"
            )

            return True

        except Exception as e:

            print(
                "[YouTube ERROR] "
                f"First video failed: {e}"
            )

            return False

    # =====================================================
    # SKIP AD
    # =====================================================

    def skip_ad(self):

        return self._run_browser(
            self._skip_ad_impl
        )

    def _skip_ad_impl(self):

        print(
            f"[Browser AD THREAD] "
            f"{threading.current_thread().name} | "
            f"{threading.get_ident()}"
        )

        if not self.page:

            return False

        try:

            for _ in range(20):

                button = (
                    self.page.get_by_text(
                        "Skip",
                        exact=True,
                    )
                )

                if button.count() > 0:

                    button.first.click()

                    print(
                        "[YouTube] Ad skipped"
                    )

                    return True

                time.sleep(0.25)

        except Exception as e:

            print(
                "[YouTube] "
                f"Skip ad failed: {e}"
            )

        print(
            "[YouTube] "
            "No skippable ad found"
        )

        return False

    # =====================================================
    # YOUTUBE KEY
    # =====================================================

    def youtube_key(self, key):

        return self._run_browser(
            self._youtube_key_impl,
            key,
        )

    def _youtube_key_impl(self, key):

        print(
            f"[Browser KEY THREAD] "
            f"{threading.current_thread().name} | "
            f"{threading.get_ident()}"
        )

        try:

            if not self._start_impl():

                return False

            if not self.browser:

                print(
                    "[YouTube] "
                    "Browser not connected"
                )

                return False

            youtube_page = None

            # -------------------------------------------------
            # Prefer tracked page
            # -------------------------------------------------

            try:

                if (
                    self.page
                    and not self.page.is_closed()
                    and "youtube.com" in self.page.url
                ):

                    youtube_page = self.page

            except Exception:

                youtube_page = None

            # -------------------------------------------------
            # Find YouTube video page
            # -------------------------------------------------

            if not youtube_page:

                for context in self.browser.contexts:

                    for page in context.pages:

                        try:

                            if (
                                "youtube.com/watch"
                                in page.url
                                and not page.is_closed()
                            ):

                                youtube_page = page

                                break

                        except Exception:

                            continue

                    if youtube_page:

                        break

            if not youtube_page:

                print(
                    "[YouTube] "
                    "YouTube video page not found"
                )

                return False

            self.page = youtube_page

            self.page.bring_to_front()

            self.page.keyboard.press(
                key
            )

            print(
                "[YouTube] "
                f"Key sent to YouTube page: {key}"
            )

            return True

        except Exception as e:

            print(
                "[YouTube CONTROL ERROR] "
                f"{e}"
            )

            return False

    # =====================================================
    # PAUSE / RESUME
    # =====================================================

    def pause_video(self):

        return self.youtube_key("k")

    def resume_video(self):

        return self.youtube_key("k")

    def fullscreen(self):

        return self.youtube_key("f")

    # =====================================================
    # NEXT VIDEO
    # =====================================================

    def next_video(self):

        return self._run_browser(
            self._next_video_impl
        )

    def _next_video_impl(self):

        try:

            if not self._start_impl():

                return False

            if not self.browser:

                return False

            youtube_page = None

            for context in self.browser.contexts:

                for page in context.pages:

                    try:

                        if (
                            "youtube.com/watch"
                            in page.url
                        ):

                            youtube_page = page

                            break

                    except Exception:

                        continue

                if youtube_page:

                    break

            if not youtube_page:

                print(
                    "[YouTube] "
                    "YouTube video page not found"
                )

                return False

            self.page = youtube_page

            self.page.bring_to_front()

            self.page.keyboard.press(
                "Shift+n"
            )

            print(
                "[YouTube] "
                "Next video command sent"
            )

            return True

        except Exception as e:

            print(
                f"[YouTube NEXT ERROR] {e}"
            )

            return False

    # =====================================================
    # PREVIOUS VIDEO
    # =====================================================

    def previous_video(self):

        return self._run_browser(
            self._previous_video_impl
        )

    def _previous_video_impl(self):

        try:

            if not self._start_impl():

                return False

            if not self.browser:

                return False

            youtube_page = None

            for context in self.browser.contexts:

                for page in context.pages:

                    try:

                        if (
                            "youtube.com/watch"
                            in page.url
                        ):

                            youtube_page = page

                            break

                    except Exception:

                        continue

                if youtube_page:

                    break

            if not youtube_page:

                print(
                    "[YouTube] "
                    "YouTube video page not found"
                )

                return False

            self.page = youtube_page

            self.page.bring_to_front()

            self.page.keyboard.press(
                "Shift+P"
            )

            print(
                "[YouTube] "
                "Previous video command sent"
            )

            return True

        except Exception as e:

            print(
                f"[YouTube PREVIOUS ERROR] {e}"
            )

            return False

    # =====================================================
    # NEW TAB
    # =====================================================

    def new_tab(self):

        return self._run_browser(
            self._new_tab_impl
        )

    def _new_tab_impl(self):

        try:

            if not self._start_impl():

                return False

            if not self.browser:

                return False

            context = self.browser.contexts[0]

            # -------------------------------------------------
            # Remember current tab
            # -------------------------------------------------

            old_page = self.page

            if (
                old_page
                and not old_page.is_closed()
            ):

                self.previous_page = old_page

            # -------------------------------------------------
            # Create new tab
            # -------------------------------------------------

            new_page = context.new_page()

            self.page = new_page

            self.page.bring_to_front()

            # -------------------------------------------------
            # Load Chrome's normal new-tab page
            # -------------------------------------------------

            try:

                self.page.goto(
                    "https://www.google.com",
                    wait_until="domcontentloaded",
                    timeout=10000,
                )

            except Exception as e:

                print(
                    f"[Browser NEW TAB] "
                    f"New-tab navigation notice: {e}"
                )

            print(
                "[Browser] "
                "New tab opened"
            )

            return True

        except Exception as e:

            print(
                f"[Browser NEW TAB ERROR] {e}"
            )

            return False

    # =====================================================
    # CLOSE TAB
    # =====================================================

    def close_tab(self):

        return self._run_browser(
            self._close_tab_impl
        )

    def _close_tab_impl(self):

        try:

            if not self.page:

                return False

            closing_page = self.page

            closing_page.close()

            # -------------------------------------------------
            # Restore previous tab if available
            # -------------------------------------------------

            if (
                self.previous_page
                and not self.previous_page.is_closed()
            ):

                self.page = self.previous_page
                self.previous_page = None

                self.page.bring_to_front()

                print(
                    "[Browser] "
                    "Returned to previous tab"
                )

            else:

                self.page = None

            return True

        except Exception as e:

            print(
                f"[Browser CLOSE TAB ERROR] {e}"
            )

            return False

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        return self._run_browser(
            self._refresh_impl
        )

    def _refresh_impl(self):

        try:

            if not self.page:

                return False

            self.page.reload()

            return True

        except Exception as e:

            print(
                f"[Browser REFRESH ERROR] {e}"
            )

            return False

    # =====================================================
    # BACK
    # =====================================================

    def back(self):

        return self._run_browser(
            self._back_impl
        )

    def _back_impl(self):

        try:

            if not self.page:

                return False

            # -------------------------------------------------
            # First: normal browser history
            # -------------------------------------------------

            response = self.page.go_back(
                wait_until="domcontentloaded",
                timeout=10000,
            )

            if response is not None:

                self.page.bring_to_front()

                print(
                    "[Browser] Navigated back"
                )

                return True

            # -------------------------------------------------
            # No history.
            #
            # This commonly happens when the current page is
            # a newly-created blank tab.
            #
            # Return to the previous JARVIS tab.
            # -------------------------------------------------

            if (
                self.previous_page
                and not self.previous_page.is_closed()
            ):

                current_page = self.page

                self.page = self.previous_page

                self.previous_page = None

                self.page.bring_to_front()

                print(
                    "[Browser] "
                    "Returned to previous tab"
                )

                # -------------------------------------------------
                # Close the temporary blank/new tab.
                # -------------------------------------------------

                try:

                    if (
                        current_page
                        and not current_page.is_closed()
                        and current_page != self.page
                    ):

                        current_page.close()

                except Exception:

                    pass

                return True

            print(
                "[Browser] "
                "No browser history or previous tab"
            )

            return False

        except Exception as e:

            print(
                f"[Browser BACK ERROR] {e}"
            )

            return False

    # =====================================================
    # FORWARD
    # =====================================================

    def forward(self):

        return self._run_browser(
            self._forward_impl
        )

    def _forward_impl(self):

        try:

            if not self.page:

                return False

            self.page.go_forward()

            return True

        except Exception as e:

            print(
                f"[Browser FORWARD ERROR] {e}"
            )

            return False

    # =====================================================
    # SCROLL DOWN
    # =====================================================

    def scroll_down(self):

        return self._run_browser(
            self._scroll_down_impl
        )

    def _scroll_down_impl(self):

        try:

            if not self.page:

                return False

            self.page.mouse.wheel(
                0,
                1000,
            )

            return True

        except Exception as e:

            print(
                f"[Browser SCROLL ERROR] {e}"
            )

            return False

    # =====================================================
    # SCROLL UP
    # =====================================================

    def scroll_up(self):

        return self._run_browser(
            self._scroll_up_impl
        )

    def _scroll_up_impl(self):

        try:

            if not self.page:

                return False

            self.page.mouse.wheel(
                0,
                -1000,
            )

            return True

        except Exception as e:

            print(
                f"[Browser SCROLL ERROR] {e}"
            )

            return False

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        return self._run_browser(
            self._close_impl
        )

    def _close_impl(self):

        try:

            if self.page:

                try:

                    self.page.close()

                except Exception:

                    pass

            if self.browser:

                try:

                    self.browser.close()

                except Exception:

                    pass

            if self.playwright:

                try:

                    self.playwright.stop()

                except Exception:

                    pass

        finally:

            self.page = None
            self.previous_page = None
            self.browser = None
            self.playwright = None

        return True


# =========================================================
# GLOBAL BROWSER INSTANCE
# =========================================================

browser = BrowserController()