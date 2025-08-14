from enum import Enum

from crawl4ai import BrowserConfig


class BrowserType(Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    EDGE = "edge"


browser_config = BrowserConfig(
    browser_type=BrowserType.CHROMIUM.value,
    headless=False,
    verbose=True,
)
