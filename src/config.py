from enum import Enum
from pathlib import Path

from crawl4ai import BrowserConfig

root_dir = Path(__file__).parent.parent
DATA_PATH = root_dir / "data"

# Create data directory if it doesn't exist
DATA_PATH.mkdir(parents=True, exist_ok=True)


class BrowserType(Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    EDGE = "edge"


browser_config = BrowserConfig(
    browser_type=BrowserType.CHROMIUM.value,
    headless=False,
    verbose=True,
)
