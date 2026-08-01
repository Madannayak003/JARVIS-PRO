from playwright.sync_api import sync_playwright


class BrowserManager:

    def __init__(self):

        self.pw = None
        self.browser = None
        self.context = None

        self.page = None

    # -------------------------

    def ensure(self):

        if self.browser:
            return

        self.pw = sync_playwright().start()

        self.browser = self.pw.chromium.launch(
            headless=False
        )

        self.context = self.browser.new_context()

    # -------------------------

    def open(self, url):

        self.ensure()

        self.page = self.context.new_page()

        self.page.goto(url)

        print("[BROWSER] New Tab")

    # -------------------------

    def search(self, url):

        self.ensure()

        if self.page is None:

            self.open(url)

            return

        self.page.goto(url)

        print("[BROWSER] Same Tab")


browser = BrowserManager()