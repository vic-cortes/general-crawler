import asyncio
import json

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.models import CrawlResultContainer

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
            {"name": "company", "selector": "p.dFlex", "type": "text"},
            {
                "name": "location",
                "selector": "p:nth-child(3)",
                "type": "text",
            },
            {
                "name": "relative_date",
                "selector": "p.fs13.fc_aux.mt15",
                "type": "text",
            },
            {
                "name": "description",
                "selector": "div.fs16.t_word_wrap",
                "type": "text",
            },
        ],
    }

    DETAIL_KEY_CSS_SELECTOR = "div:nth-child(1) > div.fs14.mb10 p"

    output_description_schema = {
        "name": "Computrabajo Job Description",
        "baseSelector": "div.box_detail",
        "fields": [
            {
                "name": "text",
                "selector": "self",
                "type": "text",
            },
        ],
    }

    SESSION_ID = "job_listings_session"

    strategy = JsonCssExtractionStrategy(output_schema)
    strategy_description = JsonCssExtractionStrategy(output_description_schema)
    crawler_config = CrawlerRunConfig(
        extraction_strategy=strategy,
        wait_for=KEY_CSS_SELECTOR,
        session_id=SESSION_ID,  # Keep session for job listings
    )

    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url=JOB_URL, config=crawler_config)

        if not result.success:
            print("Error:", result.error_message)
            return

        # Save the result to a JSON file
        offers = json.loads(result.extracted_content)

        for idx, _ in enumerate(offers):
            js = f"document.querySelectorAll('article.box_offer')[{idx}].click();"

            config_click = CrawlerRunConfig(
                js_code=js,
                wait_for=KEY_CSS_SELECTOR,
                # js_only=True,
                session_id=SESSION_ID,
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=strategy_description,
                wait_for_timeout=5_000,
            )
            result_detail = await crawler.arun(url=JOB_URL, config=config_click)
            if result_detail.success:
                detail = json.loads(result_detail.extracted_content)[idx]
                print("Detalle:", detail.get("description"))

        # for element in dict_data:
        #     element["details_url"] = f"{BASE_URL}{element['details_url']}"

        # with open("liverpool_products.json", "w") as file:
        #     json.dump(dict_data, file, indent=4)
        # print("Data saved to liverpool_products.json")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
