import asyncio
import json
from enum import Enum

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
)


class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


browser_config = BrowserConfig(browser_type=BrowserType.FIREFOX.value, headless=False)
BASE_URL = "https://www.liverpool.com.mx"
PRODUCT_URL = f"{BASE_URL}/tienda?s=lavadoras"


async def main():
    KEY_CSS_SELECTOR = "h3.a-card-brand"

    output_schema = {
        "name": "Liverpool Product Scraper",
        "baseSelector": "li.m-product__card",
        "fields": [
            {"name": "title", "selector": "h3.card-title", "type": "text"},
            {
                "name": "brand",
                "selector": "h3.a-card-brand",
                "type": "text",
            },
            {"name": "price", "selector": "p.a-card-price", "type": "text"},
            {
                "name": "details_url",
                "selector": "a",
                "type": "attribute",
                "attribute": "href",
            },
        ],
    }

    strategy = JsonCssExtractionStrategy(output_schema)
    crawler_config = CrawlerRunConfig(
        extraction_strategy=strategy,
        wait_for=KEY_CSS_SELECTOR,
    )

    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url=PRODUCT_URL, config=crawler_config)

        # Print the extracted content
        print(result.markdown)

        if result.success:
            # Save the result to a JSON file
            dict_data = json.loads(result.extracted_content)

            for element in dict_data:
                element["details_url"] = f"{BASE_URL}{element['details_url']}"

            with open("liverpool_products.json", "w") as file:
                json.dump(dict_data, file, indent=4)
            print("Data saved to liverpool_products.json")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
