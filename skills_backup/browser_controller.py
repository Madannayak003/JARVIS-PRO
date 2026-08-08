from playwright.sync_api import sync_playwright


class BrowserController:

    def __init__(self):

        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):

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

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            channel="chrome",
            headless=False
        )

        self.page = self.browser.new_page()

        print("[Browser] Chrome Started")
        
        
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
        

    def play_first_video(self):

        self.page.wait_for_selector("ytd-video-renderer")

        self.page.locator(
            "ytd-video-renderer"
        ).first.click()

    def pause_video(self):

        self.page.keyboard.press("k")

    def resume_video(self):

        self.page.keyboard.press("k")

    def fullscreen(self):

        self.page.keyboard.press("f")

    def theater_mode(self):

        self.page.keyboard.press("t")

    def next_video(self):

        self.page.keyboard.press("SHIFT+n")

    def previous_video(self):

        self.page.keyboard.press("SHIFT+p")

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