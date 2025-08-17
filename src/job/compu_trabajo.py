import asyncio
import json
import random
from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import Tag
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.models import CrawlResultContainer

from src.config import browser_config

BASE_URL = "https://mx.computrabajo.com"
ERROR_URL = "https://mx.computrabajo.com/trabajo-de-python?p=95"
JOB_URL = f"{BASE_URL}/trabajo-de-python"
KEY_CSS_SELECTOR = "#offersGridOfferContainer"
DETAIL_CSS_SELECTOR = "div.box_detail"
DETAIL_ICONS = {
    "i_clock": "time",
    "i_find": "location",
    "i_company": "place",
    "i_money": "salary",
    "i_home": "place",
}

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


def get_job_details(soup: BeautifulSoup) -> dict:
    """
    Extract job details from the job description page.
    """
    box_detail = soup.find("div", class_="box_detail")
    all_ps = box_detail.find("div", class_="fs14").find_all("p")
    description = " ".join(
        box_detail.find("div", class_="t_word_wrap").text.strip().split("\n")
    )
    requirements = box_detail.find("ul", class_="disc").text.strip()

    dict_data = {"description": description, "requirements": requirements}

    for p in all_ps:
        span_class = "__".join(p.find("span").attrs.get("class"))
        text = p.text.strip()

        for icon_class, key in DETAIL_ICONS.items():
            if icon_class in span_class:
                dict_data[key] = text
                break

    return dict_data


BASE_SELECTOR = "article.box_offer"


class MainPageSetup:

    def __init__(self):
        self._base_selector = "article.box_offer"

    @property
    def session_id(self) -> str:
        """
        Generate a unique session ID for the scraper.
        """
        return None

    @property
    def service_name(self) -> str:
        return "compu_trabajo"

    def _output_schema(self):
        return {
            "name": self.service_name + " Job Scraper",
            "baseSelector": BASE_SELECTOR,
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

    def _get_crawler_config(self):
        strategy = JsonCssExtractionStrategy(self._output_schema())

        return CrawlerRunConfig(
            extraction_strategy=strategy,
            wait_for=KEY_CSS_SELECTOR,
            session_id=self.session_id,
            wait_for_timeout=2_000,
        )


@dataclass
class Scraper(MainPageSetup):
    url: str
    crawler: AsyncWebCrawler

    @property
    def session_id(self) -> str:
        return f"{self.service_name}_scraper_{random.randint(1000, 9999)}"

    async def _get_overview(self) -> dict | None:
        result = await self.crawler.arun(
            url=self.url,
            config=self._get_crawler_config(),
        )

        if not result.success:
            print("Error:", result.error_message)
            return False

        return json.loads(result.extracted_content)

    async def _get_details(self, idx: int, offer: dict) -> dict:
        """
        Retrieve details from the page
        """
        js = f"document.querySelectorAll('article.box_offer')[{idx}].click();"

        config_click = CrawlerRunConfig(
            js_code=js,
            wait_for=DETAIL_CSS_SELECTOR,
            session_id=self.session_id,
            cache_mode=CacheMode.ENABLED,
            wait_for_timeout=5_000,
        )
        result_detail = await self.crawler.arun(url=JOB_URL, config=config_click)

        if result_detail.success:
            # We use bs4 because the complex structure of the job details
            soup = BeautifulSoup(result_detail.html, "html.parser")
            offer["details"] = get_job_details(soup)

        return offer

    async def click_next_page(self) -> CrawlResultContainer:
        """
        Click the next page button
        """
        js_next = [
            "console.log('dummy')",
            "document.querySelector('span.b_primary.w48.buildLink.cp').click();",
        ]

        config_click_next = CrawlerRunConfig(
            js_code=js_next,
            js_only=True,
            wait_for=DETAIL_CSS_SELECTOR,
            session_id=self.session_id,
            wait_for_timeout=5_000,
        )
        return await self.crawler.arun(url=JOB_URL, config=config_click_next)

    async def get_data(self):
        """
        Retrieve job data from the website.
        """

        if not (offers := await self._get_overview()):
            return None

        for idx, offer in enumerate(offers):
            offers[idx] = await self._get_details(idx, offer)

        return offers


async def dummy():
    async with AsyncWebCrawler(config=browser_config) as crawler:
        offers = {}
        scraper = Scraper(url=JOB_URL, crawler=crawler)

        while offers is not None:
            offers = await scraper.get_data()


async def main():
    # random number
    random_number = random.randint(1000, 9999)
    SESSION_ID = f"job_listings_session_{random_number}"

    strategy = JsonCssExtractionStrategy(output_schema)

    crawler_config = CrawlerRunConfig(
        extraction_strategy=strategy,
        wait_for=KEY_CSS_SELECTOR,
        session_id=SESSION_ID,  # Keep session for job listings
        wait_for_timeout=5_000,
    )

    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url=ERROR_URL, config=crawler_config)

        if not result.success:
            print("Error:", result.error_message)
            return

        # Save the result to a JSON file
        offers = json.loads(result.extracted_content)

        for idx, _ in enumerate(offers):
            js = f"document.querySelectorAll('article.box_offer')[{idx}].click();"

            config_click = CrawlerRunConfig(
                js_code=js,
                wait_for=DETAIL_CSS_SELECTOR,
                session_id=SESSION_ID,
                cache_mode=CacheMode.ENABLED,
                wait_for_timeout=5_000,
            )
            result_detail = await crawler.arun(url=JOB_URL, config=config_click)

            if result_detail.success:
                # We use bs4 because the complex structure of the job details
                soup = BeautifulSoup(result_detail.html, "html.parser")
                dict_data = get_job_details(soup)
                offers[idx]["details"] = dict_data

        # Click next page
        js_next = [
            "console.log('dummy')",
            "document.querySelector('span.b_primary.w48.buildLink.cp').click();",
        ]

        config_click_next = CrawlerRunConfig(
            js_code=js_next,
            js_only=True,
            wait_for=DETAIL_CSS_SELECTOR,
            session_id=SESSION_ID,
            wait_for_timeout=5_000,
        )
        result_detail = await crawler.arun(url=JOB_URL, config=config_click_next)
        result_detail = await crawler.arun(url=JOB_URL, config=config_click_next)

        print(offers)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
