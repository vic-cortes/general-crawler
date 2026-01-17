import asyncio

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler

from src.job.mixins import BaseScraper, ConcurrentScraperMixin

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


class OCCScraper(BaseScraper):
    """
    Scraper específico para OCC.com.mx
    """

    @property
    def service_name(self) -> str:
        return "occ"

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

    def _get_salary(self) -> str | None:
        """Extract the salary information from the job details."""
        for span in self.box_detail.find_all("span"):
            if span.attrs and "i_money" in span.attrs.get("class", []):
                return span.parent.text.strip()

    def _get_description(self) -> str | None:
        """Extract the job description from the job details."""
        DESCRIPTION = "descripción"
        all_ps = self.box_detail.find_all("p")

        description_tag = [el for el in all_ps if DESCRIPTION in el.text.lower()]

        if not description_tag:
            return {}

        description_tag = description_tag[0]
        return description_tag.parent.text.strip()

    def _get_offer_id(self, soup: BeautifulSoup) -> str | None:
        """Extract the job ID from the job details."""
        JOB_ID = "id:"
        all_ps = self.box_detail.find_all("p")

        job_id_tag = [el for el in all_ps if JOB_ID in el.text.lower()]

        if not job_id_tag:
            return None

        return job_id_tag[0].text.split()[-1]

    def _get_requirements(self) -> str | None:
        """Extract the job requirements from the job details."""
        REQUIREMENTS = "requisitos"
        all_ps = self.box_detail.find_all("p")

        requirements_tag = [el for el in all_ps if REQUIREMENTS in el.text.lower()]

        if not requirements_tag:
            return None

        requirements_tag = requirements_tag[0].find_next_sibling()
        return requirements_tag.text

    def get_job_details(self, soup: BeautifulSoup) -> dict:
        """Extract job details from the job description page."""
        DETAIL_SELECTOR = "job-detail-container"
        job_url = None

        self.box_detail = soup.find(id=DETAIL_SELECTOR)

        salary = self._get_salary()
        description = self._get_description()
        job_id = self._get_offer_id(soup)
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

    async def is_next_page_available(self) -> bool:
        """Check if the next page is available."""
        from crawl4ai import CrawlerRunConfig

        config_click_next = CrawlerRunConfig(session_id=self.session_id)
        result = await self.crawler.arun(url=self.url, config=config_click_next)

        soup = BeautifulSoup(result.html, "html.parser")
        next_page_button = soup.select_one("#btn-next-offer")
        return bool(next_page_button)


class OCCConcurrentScraper(ConcurrentScraperMixin):
    """
    Scraper concurrente para OCC usando el mixin.
    """

    @classmethod
    async def run(cls, max_pages: int = 100, max_concurrent_browsers: int = 3):
        """
        Ejecuta el scraping concurrente de OCC.

        Args:
            max_pages: Número máximo de páginas a scrapear
            max_concurrent_browsers: Número máximo de browsers concurrentes
        """
        await cls.main_scraper(
            scraper_class=OCCScraper,
            base_job_url=JOB_URL,
            url_pattern=f"{JOB_URL}?page={{page_num}}",
            max_pages=max_pages,
            max_concurrent_browsers=max_concurrent_browsers,
        )


async def main_scraper(max_pages: int = 100, max_concurrent_browsers: int = 3):
    """
    Función principal de scraping para mantener compatibilidad.
    """
    await OCCConcurrentScraper.run(max_pages, max_concurrent_browsers)


if __name__ == "__main__":
    # Run with default settings: max 100 pages, max 3 concurrent browsers
    asyncio.run(main_scraper())
