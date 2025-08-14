from enum import Enum

from crawl4ai import BrowserConfig


class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


browser_config = BrowserConfig(browser_type=BrowserType.FIREFOX.value, headless=False)
