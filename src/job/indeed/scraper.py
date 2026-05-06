import asyncio
import json
import re
from datetime import datetime

from bs4 import BeautifulSoup
from crawl4ai import CrawlerRunConfig

from src.config import DATA_PATH
from src.job.mixins import BaseScraper, ConcurrentScraperMixin

INDEED_BASE_URL = "https://mx.indeed.com"
KEY_CSS_SELECTOR = "#mosaic-provider-jobcards"
DETAIL_CSS_SELECTOR = ".jobsearch-ViewJobLayout--embedded"
BASE_SELECTOR = "div.job_seen_beacon"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
RESULTS_PER_PAGE = 10


class IndeedScraper(BaseScraper):
    """
    Scraper específico para Indeed.
    """

    @property
    def service_name(self) -> str:
        return "indeed"

    @property
    def base_selector(self) -> str:
        return BASE_SELECTOR

    @property
    def key_css_selector(self) -> str:
        return KEY_CSS_SELECTOR

    @property
    def detail_css_selector(self) -> str:
        return DETAIL_CSS_SELECTOR

    @property
    def date_format(self) -> str:
        return DATE_FORMAT

    def _output_schema(self):
        return {
            "name": self.service_name + " Job Scraper",
            "baseSelector": BASE_SELECTOR,
            "fields": [
                {"name": "title", "selector": "span[id^=jobTitle]", "type": "text"},
                {
                    "name": "company",
                    "selector": "[data-testid='company-name']",
                    "type": "text",
                },
                {
                    "name": "location",
                    "selector": "[data-testid='text-location']",
                    "type": "text",
                },
                {
                    "name": "salary",
                    "selector": "[data-testid='attribute_snippet_testid']",
                    "type": "text",
                },
                {
                    "name": "job_key",
                    "selector": "a.jcs-JobTitle",
                    "type": "attribute",
                    "attribute": "data-jk",
                },
            ],
        }

    def get_job_details(self, soup: BeautifulSoup) -> dict:
        """Extract job details from the right-side detail panel."""
        panel = soup.select_one(DETAIL_CSS_SELECTOR)
        if not panel:
            return {}

        company_el = panel.select_one("[data-testid='inlineHeader-companyName']")
        location_el = panel.select_one("[data-testid='inlineHeader-companyLocation']")
        salary_el = panel.select_one(
            "[data-testid='jobsearch-OtherJobDetailsContainer']"
        )
        desc_el = panel.select_one("#jobDescriptionText")

        job_url = None
        for a in panel.select("a[href*='fromjk=']"):
            match = re.search(r"fromjk=([a-zA-Z0-9]+)", a.get("href", ""))
            if match:
                job_url = f"{INDEED_BASE_URL}/viewjob?jk={match.group(1)}"
                break

        return {
            "company": company_el.text.strip() if company_el else "",
            "location": location_el.text.strip() if location_el else "",
            "salary": salary_el.text.strip() if salary_el else "",
            "description": desc_el.text.strip() if desc_el else "",
            "job_url": job_url,
        }

    def _get_offer_id(self, soup: BeautifulSoup) -> str | None:
        """Extract job offer ID from the detail panel company link."""
        panel = soup.select_one(DETAIL_CSS_SELECTOR)
        if not panel:
            return None
        for a in panel.select("a[href*='fromjk=']"):
            match = re.search(r"fromjk=([a-zA-Z0-9]+)", a.get("href", ""))
            if match:
                return match.group(1)
        return None

    async def is_next_page_available(self) -> bool:
        """Check if the next page is available."""
        config = CrawlerRunConfig(session_id=self.session_id)
        result = await self.crawler.arun(url=self.url, config=config)
        soup = BeautifulSoup(result.html, "html.parser")
        return bool(soup.select_one("a[data-testid='pagination-page-next']"))


class IndeedConcurrentScraper(ConcurrentScraperMixin):
    """
    Scraper concurrente para Indeed usando el mixin.
    """

    @classmethod
    async def run(
        cls,
        job_title: str = "python",
        location: str = "Mexico",
        max_pages: int = 100,
        max_concurrent_browsers: int = 3,
    ):
        """
        Ejecuta el scraping concurrente de Indeed.

        Indeed usa paginación por offset (start=0, 10, 20…) en lugar de número de página,
        por lo que se construyen las URLs manualmente antes de llamar a scrape_page.

        Args:
            job_title: Término de búsqueda de trabajo
            location: Ubicación para la búsqueda
            max_pages: Número máximo de páginas a scrapear
            max_concurrent_browsers: Número máximo de browsers concurrentes
        """
        base_url = (
            f"{INDEED_BASE_URL}/jobs"
            f"?q={job_title.replace(' ', '+')}"
            f"&l={location.replace(' ', '+')}"
        )
        semaphore = asyncio.Semaphore(max_concurrent_browsers)

        tasks = [cls.scrape_page(IndeedScraper, base_url, semaphore, 1)]
        for page_num in range(2, max_pages + 1):
            start = (page_num - 1) * RESULTS_PER_PAGE
            page_url = f"{base_url}&start={start}"
            tasks.append(cls.scrape_page(IndeedScraper, page_url, semaphore, page_num))

        print(
            f"Starting Indeed scraper with max {max_concurrent_browsers} concurrent browsers"
        )
        print(f"Launching {len(tasks)} concurrent scraping tasks...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_offers = []
        successful_pages = 0
        for i, result in enumerate(results):
            page_num = i + 1
            if isinstance(result, Exception):
                print(f"Page {page_num} failed with exception: {result}")
            elif result is None:
                print(f"Page {page_num} returned None")
            elif isinstance(result, list):
                all_offers.extend(result)
                successful_pages += 1
                print(f"Page {page_num}: added {len(result)} offers")

        print(
            f"Scraping completed. Processed {successful_pages} pages, "
            f"found {len(all_offers)} total offers"
        )

        if not all_offers:
            print("No offers found. Exiting without creating file.")
            return

        current_time = datetime.now().strftime("%Y%m%d_%H_00")
        file_name = DATA_PATH / f"indeed_job_offers_{current_time}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(all_offers, f, indent=4, ensure_ascii=False)
        print(f"Results saved to: {file_name}")
        print(f"Total offers scraped: {len(all_offers)}")


async def main_scraper(
    job_title: str = "python",
    location: str = "Mexico",
    max_pages: int = 100,
    max_concurrent_browsers: int = 3,
):
    """
    Función principal de scraping para mantener compatibilidad.
    """
    await IndeedConcurrentScraper.run(
        job_title, location, max_pages, max_concurrent_browsers
    )


if __name__ == "__main__":
    asyncio.run(main_scraper(max_pages=50, max_concurrent_browsers=7))
