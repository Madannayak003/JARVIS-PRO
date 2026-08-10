from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()

options.add_experimental_option(
    "debuggerAddress",
    "127.0.0.1:9223"
)

driver = webdriver.Chrome(options=options)

driver.get("https://web.whatsapp.com")

input("Press Enter...")