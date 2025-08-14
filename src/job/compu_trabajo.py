import asyncio
import json

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, JsonCssExtractionStrategy

from src.config import browser_config

BASE_URL = "https://mx.computrabajo.com"
JOB_URL = f"{BASE_URL}/trabajo-de-python"


async def main():
    KEY_CSS_SELECTOR = "#offersGridOfferContainer"

    output_schema = {
        "name": "Computrabajo Job Scraper",
        "baseSelector": "article.box_offer",
        "fields": [
            {"name": "title", "selector": "a.js-o-link", "type": "text"},
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
        result = await crawler.arun(url=JOB_URL, config=crawler_config)

        # Print the extracted content
        # print(result.markdown)

        if result.success:
            # Save the result to a JSON file
            dict_data = json.loads(result.extracted_content)

            # for element in dict_data:
            #     element["details_url"] = f"{BASE_URL}{element['details_url']}"

            # with open("liverpool_products.json", "w") as file:
            #     json.dump(dict_data, file, indent=4)
            # print("Data saved to liverpool_products.json")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
