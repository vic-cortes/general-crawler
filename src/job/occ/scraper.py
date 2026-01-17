import asyncio
import json
import random
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

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
        return f"{self.service_name}_scraper_{id(self.crawler)}"

    def set_url(self, url: str) -> None:
        self.url = url

    async def _get_overview(self) -> dict | None:
        result = await self.crawler.arun(
            url=self.url,
            config=self._get_crawler_config(),
        )

        if not result.success:
            print("Error:", result.error_message)
            return False

        return json.loads(result.extracted_content)

    def _get_salary(self) -> str | None:
        """
        Extract the salary information from the job details.
        """

        for span in self.box_detail.find_all("span"):
            if span.attrs and "i_money" in span.attrs.get("class", []):
                return span.parent.text.strip()

    def _get_description(self) -> str | None:
        """
        Extract the job description from the job details.
        """
        DESCRIPTION = "descripción"
        all_ps = self.box_detail.find_all("p")

        description_tag = [el for el in all_ps if DESCRIPTION in el.text.lower()]

        if not description_tag:
            return {}

        description_tag = description_tag[0]
        return description_tag.parent.text.strip()

    def _get_offer_id(self) -> str | None:
        """
        Extract the job ID from the job details.
        """
        JOB_ID = "id:"
        all_ps = self.box_detail.find_all("p")

        job_id_tag = [el for el in all_ps if JOB_ID in el.text.lower()]

        if not job_id_tag:
            return None

        return job_id_tag[0].text.split()[-1]

    def _get_requirements(self) -> str | None:
        """
        Extract the job requirements from the job details.
        """
        REQUIREMENTS = "requisitos"
        all_ps = self.box_detail.find_all("p")

        requirements_tag = [el for el in all_ps if REQUIREMENTS in el.text.lower()]

        if not requirements_tag:
            return None

        requirements_tag = requirements_tag[0].find_next_sibling()
        return requirements_tag.text

    def get_job_details(self, soup: BeautifulSoup) -> dict:
        """
        Extract job details from the job description page.
        """
        DETAIL_SELECTOR = "job-detail-container"
        job_url = None

        self.box_detail = soup.find(id=DETAIL_SELECTOR)

        salary = self._get_salary()
        description = self._get_description()
        job_id = self._get_offer_id()
        requirements = self._get_requirements()

        if job_id:
            job_url = f"{BASE_URL}/empleo/oferta/{job_id}/"

        dict_data = {
            "description": description,
            "job_url": job_url,
            "salary": salary,
            "requirements": requirements,
        }

        return dict_data

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
            offer["details"] = self.get_job_details(soup)
            offer["offer_id"] = self._get_offer_id()
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
        next_page_button = soup.select_one("#btn-next-offer")
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


async def scrape_page(
    url: str, semaphore: asyncio.Semaphore, page_num: int
) -> Optional[List[dict]]:
    """
    Scrape a single page with its own browser instance.

    Args:
        url: The URL to scrape
        semaphore: Semaphore to limit concurrent browser instances
        page_num: Page number for logging purposes

    Returns:
        List of job offers or None if failed
    """
    async with semaphore:
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                scraper = Scraper(url=url, crawler=crawler)
                print(f"Starting scrape of page {page_num}: {url}")

                # Check if page exists before scraping
                if page_num > 1 and not await scraper.is_next_page_available:
                    print(f"Page {page_num} not available, stopping.")
                    return None

                offers = await scraper.get_data()
                if offers:
                    print(f"Completed page {page_num}: found {len(offers)} offers")
                    return offers
                else:
                    print(f"Page {page_num}: no offers found")
                    return []

        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            return []


async def main_scraper(max_pages: int = 100, max_concurrent_browsers: int = 3):
    """
    Enhanced main scraper with concurrent execution.

    Args:
        max_pages: Maximum number of pages to scrape
        max_concurrent_browsers: Maximum number of concurrent browser instances
    """
    print(
        f"Starting async scraper with max {max_concurrent_browsers} concurrent browsers"
    )

    # Create semaphore to limit concurrent browser instances
    semaphore = asyncio.Semaphore(max_concurrent_browsers)

    # Prepare tasks for concurrent execution
    tasks = []

    # First page (base URL)
    tasks.append(scrape_page(JOB_URL, semaphore, 1))

    # Additional pages
    for page_num in range(2, max_pages + 1):
        page_url = f"{JOB_URL}?page={page_num}"
        tasks.append(scrape_page(page_url, semaphore, page_num))

    # Execute all tasks concurrently
    print(f"Launching {len(tasks)} concurrent scraping tasks...")
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    all_offers = []
    successful_pages = 0

    for i, result in enumerate(results):
        page_num = i + 1

        if isinstance(result, Exception):
            print(f"Page {page_num} failed with exception: {result}")
        elif result is None:
            print(f"Page {page_num} returned None (likely no more pages)")
            # Stop processing further pages when we hit None
            break
        elif isinstance(result, list):
            all_offers.extend(result)
            successful_pages += 1
            print(f"Page {page_num}: added {len(result)} offers")

    print(
        f"Scraping completed. Processed {successful_pages} pages, found {len(all_offers)} total offers"
    )

    if not all_offers:
        print("No offers found. Exiting without creating file.")
        return

    # Save all offers to a JSON file
    current_time = datetime.now().strftime("%Y%m%d_%H_00")
    service_name = "occ"
    file_name = DATA_PATH / f"{service_name}_job_offers_{current_time}.json"

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(all_offers, f, indent=4, ensure_ascii=False)

    print(f"Results saved to: {file_name}")
    print(f"Total offers scraped: {len(all_offers)}")


if __name__ == "__main__":
    # Run with default settings: max 100 pages, max 3 concurrent browsers
    asyncio.run(main_scraper())
