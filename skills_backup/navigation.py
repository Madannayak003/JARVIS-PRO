import webbrowser
import urllib.parse


class NavigationEngine:

    def open(self, url):

        print(f"[NAVIGATION] {url}")

        webbrowser.open(url)

    def google(self, query):

        url = (
            "https://www.google.com/search?q="
            + urllib.parse.quote(query)
        )

        self.open(url)

    def youtube(self, query):

        url = (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote(query)
        )

        self.open(url)
        
    def github(self, query):

        url = (
            "https://github.com/search?q="
            + urllib.parse.quote(query)
        )

        self.open(url)


    def chatgpt(self, query):

        url = (
            "https://chat.openai.com/?q="
            + urllib.parse.quote(query)
        )

        self.open(url)


navigation = NavigationEngine()