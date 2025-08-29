import asyncio
import json
import random
from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.models import CrawlResultContainer

from src.config import DATA_PATH, browser_config

BASE_URL = "https://www.occ.com.mx"
JOB_URL = f"{BASE_URL}/empleos/de-python/"
KEY_CSS_SELECTOR = "aside.col-span-12"
DETAIL_CSS_SELECTOR = "#job-detail-container"
DETAIL_ICONS = {
    "i_clock": "time",
    "i_find": "location",
    "i_company": "place",
    "i_money": "salary",
    "i_home": "place",
}
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

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
    box_detail = soup.find(id="job-detail-container")
    job_url = None

    description_tag = [
        el for el in box_detail.find_all("p") if "descripción" in el.text.lower()
    ]

    if not description_tag:
        return {}

    description_tag = description_tag[0]
    description = description_tag.parent.text.strip()
    id_tag = [el for el in box_detail.find_all("p") if "id:" in el.text.lower()]

    if id_tag:
        id = id_tag[0].text.split()[-1]
        job_url = f"{BASE_URL}/empleo/oferta/{id}/"

    dict_data = {
        "description": description,
        "job_url": job_url,
    }

    return dict_data


BASE_SELECTOR = "div.bg-bg-surface-default"


class MainPageSetup:

    @property
    def session_id(self) -> str:
        """
        Generate a unique session ID for the scraper.
        """
        return None

    @property
    def service_name(self) -> str:
        return "occ"

    def _output_schema(self):
        return {
            "name": self.service_name + " Job Scraper",
            "baseSelector": BASE_SELECTOR,
            "fields": [
                {"name": "title", "selector": "h2.text-grey-900", "type": "text"},
                {
                    "name": "company",
                    "selector": "span.line-clamp-title",
                    "type": "text",
                },
                {
                    "name": "location",
                    "selector": "div.no-alter-loc-text.mt-1 > p",
                    "type": "text",
                },
                {
                    "name": "relative_date",
                    "selector": "div > div.flex.items-center.justify-between.mb-2 > div > span",
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
        return f"{self.service_name}_scraper"

    def set_url(self, url: str) -> None:
        self.url = url

    def _get_offer_id(self, soup: BeautifulSoup) -> str | None:
        """
        Extract the job offer ID from the URL.
        """
        id_tag = [el for el in soup.find_all("p") if "id:" in el.text.lower()]
        return

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
        js = f"document.querySelectorAll('{BASE_SELECTOR}')[{idx}].click();"

        config_click = CrawlerRunConfig(
            js_code=js,
            js_only=True,
            wait_for="#btn-apply",
            session_id=self.session_id,
            wait_for_timeout=5_000,
        )
        result_detail = await self.crawler.arun(url=self.url, config=config_click)

        if result_detail.success:
            # We use bs4 because the complex structure of the job details
            soup = BeautifulSoup(result_detail.html, "html.parser")
            offer["details"] = get_job_details(soup)
            offer["offer_id"] = self._get_offer_id(soup)
            offer["current_datetime"] = datetime.now().strftime(DATE_FORMAT)

        return offer

    async def click_next_page(self) -> CrawlResultContainer:
        """
        Click the next page button
        """
        js_next = "document.querySelector('span.b_primary.w48.buildLink.cp').click();"

        config_click_next = CrawlerRunConfig(
            js_code=js_next,
            js_only=True,
            wait_for=DETAIL_CSS_SELECTOR,
            session_id=self.session_id,
            wait_for_timeout=5_000,
        )
        return await self.crawler.arun(url=self.url, config=config_click_next)

    @property
    async def is_next_page_available(self) -> bool:
        """
        Check if the next page is available.
        """
        config_click_next = CrawlerRunConfig(session_id=self.session_id)

        result = await self.crawler.arun(url=self.url, config=config_click_next)

        soup = BeautifulSoup(result.html, "html.parser")
        next_page_button = soup.select_one(DETAIL_CSS_SELECTOR)
        return bool(next_page_button)

    async def get_data(self):
        """
        Retrieve job data from the website.
        """

        if not (offers := await self._get_overview()):
            return None

        for idx, offer in enumerate(offers):
            try:
                offers[idx] = await self._get_details(idx, offer)
            except Exception as e:
                print(f"Error retrieving details for offer {idx}: {e}")

        return offers


async def main_scraper():
    async with AsyncWebCrawler(config=browser_config) as crawler:
        scraper = Scraper(url=JOB_URL, crawler=crawler)
        # Initial chunk
        all_offers = await scraper.get_data()

        for url_idx in range(2, 100):
            new_url = f"{JOB_URL}?p={url_idx}"
            scraper.set_url(new_url)
            if not await scraper.is_next_page_available:
                break
            offers = await scraper.get_data()
            all_offers.extend(offers)

    # Save all offers to a JSON file
    current_time = datetime.now().strftime("%Y%m%d_%H_00")
    file_name = DATA_PATH / f"{scraper.service_name}_job_offers_{current_time}.json"

    with open(file_name, "w") as f:
        json.dump(all_offers, f, indent=4)


async def get_details(
    crawler: AsyncWebCrawler, url: str, session_id: str, idx: int, offer: dict
) -> dict:
    """
    Retrieve details from the page
    """
    js = f"document.querySelectorAll('article.box_offer')[{idx}].click();"

    config_click = CrawlerRunConfig(
        js_code=js,
        js_only=True,
        wait_for=DETAIL_CSS_SELECTOR,
        session_id=session_id,
        wait_for_timeout=5_000,
    )
    result_detail = await crawler.arun(url=url, config=config_click)

    if result_detail.success:
        # We use bs4 because the complex structure of the job details
        soup = BeautifulSoup(result_detail.html, "html.parser")
        offer["details"] = get_job_details(soup)
        # offer["offer_id"] = self._get_offer_id(soup)
        offer["current_datetime"] = datetime.now().strftime(DATE_FORMAT)

    return offer


if __name__ == "__main__":
    asyncio.run(main_scraper())
