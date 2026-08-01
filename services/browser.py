from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config.browser import (
    CHROME_PROFILE,
    HEADLESS
)

_driver = None


def get_driver():

    global _driver

    if _driver is not None:
        return _driver

    options = webdriver.ChromeOptions()

    options.add_argument(
        f"--user-data-dir={CHROME_PROFILE}"
    )

    options.add_argument("--start-maximized")

    options.add_argument("--disable-notifications")

    options.add_argument("--no-first-run")

    options.add_argument("--disable-popup-blocking")

    if HEADLESS:
        options.add_argument("--headless=new")

    _driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    return _driver


def open_url(url):

    driver = get_driver()

    driver.get(url)

    return driver


def close_browser():

    global _driver

    if _driver:

        _driver.quit()

        _driver = None