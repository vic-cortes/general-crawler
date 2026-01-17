import asyncio

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler

from src.job.mixins import BaseScraper, ConcurrentScraperMixin

BASE_URL = "https://mx.computrabajo.com"
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
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
BASE_SELECTOR = "article.box_offer"


class ComputTrabajoScraper(BaseScraper):
    """
    Scraper específico para ComputTrabajo.com
    """

    @property
    def service_name(self) -> str:
        return "compu_trabajo"

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

    def get_job_details(self, soup: BeautifulSoup) -> dict:
        """Extract job details from the job description page."""
        box_detail = soup.find("div", class_="box_detail")

        if not box_detail:
            return {}

        fs14_div = box_detail.find("div", class_="fs14")
        job_url = None

        if not fs14_div:
            return {}

        if bubble := box_detail.find("div", class_="opt_bubble"):
            job_url = f"{BASE_URL}{bubble.attrs['data-url']}"

        all_ps = fs14_div.find_all("p")

        # Handle description safely
        description = ""
        if desc_div := box_detail.find("div", class_="t_word_wrap"):
            description = " ".join(desc_div.text.strip().split("\n"))

        # Handle requirements safely
        requirements = ""
        if req_ul := box_detail.find("ul", class_="disc"):
            requirements = req_ul.text.strip()

        dict_data = {
            "description": description,
            "requirements": requirements,
            "job_url": job_url,
        }

        for p in all_ps:
            span = p.find("span")
            if not span or not span.attrs:
                continue

            span_class = "__".join(span.attrs.get("class", []))
            text = p.text.strip()

            for icon_class, key in DETAIL_ICONS.items():
                if icon_class in span_class:
                    dict_data[key] = text
                    break

        return dict_data

    def _get_offer_id(self, soup: BeautifulSoup) -> str | None:
        """Extract the job offer ID from the URL."""
        id_offer_elem = soup.find(id="IdOffer")
        if id_offer_elem:
            return id_offer_elem.attrs.get("value")
        return None

    async def is_next_page_available(self) -> bool:
        """Check if the next page is available."""
        from crawl4ai import CrawlerRunConfig

        config_click_next = CrawlerRunConfig(session_id=self.session_id)
        result = await self.crawler.arun(url=self.url, config=config_click_next)

        soup = BeautifulSoup(result.html, "html.parser")
        # Check for offers container instead of detail selector
        offers_container = soup.select_one(KEY_CSS_SELECTOR)
        return bool(offers_container and soup.select("article.box_offer"))


class ComputTrabajoConcurrentScraper(ConcurrentScraperMixin):
    """
    Scraper concurrente para ComputTrabajo usando el mixin.
    """

    @classmethod
    async def run(cls, max_pages: int = 100, max_concurrent_browsers: int = 3):
        """
        Ejecuta el scraping concurrente de ComputTrabajo.

        Args:
            max_pages: Número máximo de páginas a scrapear
            max_concurrent_browsers: Número máximo de browsers concurrentes
        """
        await cls.main_scraper(
            scraper_class=ComputTrabajoScraper,
            base_job_url=JOB_URL,
            url_pattern=f"{JOB_URL}?p={{page_num}}",
            max_pages=max_pages,
            max_concurrent_browsers=max_concurrent_browsers,
        )


async def main_scraper(max_pages: int = 100, max_concurrent_browsers: int = 3):
    """
    Función principal de scraping para mantener compatibilidad.
    """
    await ComputTrabajoConcurrentScraper.run(max_pages, max_concurrent_browsers)


if __name__ == "__main__":
    # Run with default settings: max 100 pages, max 3 concurrent browsers
    asyncio.run(main_scraper(max_pages=50))
