from core.registry import register
from skills.browser.browser_controller import browser

register("refresh", lambda data: browser.refresh())
register("back", lambda data: browser.back())
register("forward", lambda data: browser.forward())
register("new_tab", lambda data: browser.new_tab())
register("close_tab", lambda data: browser.close_tab())
register("close", lambda data: browser.close())
register("scroll_down", lambda data: browser.scroll_down())
register("scroll_up", lambda data: browser.scroll_up())