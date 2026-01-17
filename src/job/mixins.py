"""
Mixins para funcionalidad compartida entre scrapers de trabajo.

Este módulo contiene clases base que pueden ser heredadas por scrapers específicos
para compartir funcionalidad común como configuración de crawlers, ejecución asíncrona
y procesamiento concurrente.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

from src.config import DATA_PATH, browser_config


class BaseScraperSetup(ABC):
    """
    Clase base abstracta para configuración de scrapers.

    Define la interfaz común que deben implementar todos los scrapers.
    """

    @property
    def session_id(self) -> str:
        """
        Generate a unique session ID for the scraper.
        """
        return None

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Nombre del servicio de empleo que se está scrapeando."""
        pass

    @property
    @abstractmethod
    def base_selector(self) -> str:
        """Selector CSS base para elementos de ofertas de trabajo."""
        pass

    @property
    @abstractmethod
    def key_css_selector(self) -> str:
        """Selector CSS para esperar a que cargue la página."""
        pass

    @abstractmethod
    def _output_schema(self) -> dict:
        """Esquema de salida para la extracción de datos."""
        pass

    def _get_crawler_config(self):
        """Configuración común del crawler."""
        strategy = JsonCssExtractionStrategy(self._output_schema())

        return CrawlerRunConfig(
            extraction_strategy=strategy,
            wait_for=self.key_css_selector,
            session_id=self.session_id,
            wait_for_timeout=2_000,
        )


class AsyncScraperMixin:
    """
    Mixin que proporciona funcionalidad asíncrona común para scrapers.

    Incluye métodos para obtener overview de páginas, manejo de URLs,
    y funcionalidad de navegación básica.
    """

    def set_url(self, url: str) -> None:
        """Establece la URL a scrapear."""
        self.url = url

    async def _get_overview(self) -> dict | None:
        """
        Obtiene el overview de ofertas de una página.

        Returns:
            Dict con las ofertas extraídas o None si hay error
        """
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
        Obtiene detalles de una oferta específica haciendo click en ella.

        Args:
            idx: Índice de la oferta en la página
            offer: Dict de la oferta a enriquecer

        Returns:
            Dict de la oferta enriquecida con detalles
        """
        js = f"document.querySelectorAll('{self.base_selector}')[{idx}].click();"

        config_click = CrawlerRunConfig(
            js_code=js,
            js_only=True,
            wait_for=self.detail_css_selector,
            session_id=self.session_id,
            wait_for_timeout=5_000,
        )
        result_detail = await self.crawler.arun(url=self.url, config=config_click)

        if result_detail.success:
            # Usar bs4 por la estructura compleja de los detalles
            soup = BeautifulSoup(result_detail.html, "html.parser")
            offer["details"] = self.get_job_details(soup)
            offer["offer_id"] = self._get_offer_id(soup)
            offer["current_datetime"] = datetime.now().strftime(self.date_format)

        return offer

    async def get_data(self):
        """
        Método principal para obtener todos los datos de una página.

        Returns:
            Lista de ofertas con detalles o None si hay error
        """
        if not (offers := await self._get_overview()):
            return None

        for idx, offer in enumerate(offers):
            try:
                offers[idx] = await self._get_details(idx, offer)
            except Exception as e:
                print(f"Error retrieving details for offer {idx}: {e}")

        return offers

    @abstractmethod
    async def is_next_page_available(self) -> bool:
        """Verifica si hay una siguiente página disponible."""
        pass

    @abstractmethod
    def get_job_details(self, soup: BeautifulSoup) -> dict:
        """Extrae detalles específicos del trabajo desde el HTML."""
        pass

    @abstractmethod
    def _get_offer_id(self, soup: BeautifulSoup) -> str | None:
        """Extrae el ID de la oferta desde el HTML."""
        pass


@dataclass
class BaseScraper(BaseScraperSetup, AsyncScraperMixin):
    """
    Clase base que combina configuración y funcionalidad asíncrona.

    Args:
        url: URL base a scrapear
        crawler: Instancia del AsyncWebCrawler
    """

    url: str
    crawler: AsyncWebCrawler

    @property
    def session_id(self) -> str:
        return f"{self.service_name}_scraper_{id(self.crawler)}"


class ConcurrentScraperMixin:
    """
    Mixin que proporciona funcionalidad de scraping concurrente.

    Implementa el patrón de semáforo para controlar browsers concurrentes
    y manejo de múltiples páginas en paralelo.
    """

    @staticmethod
    async def scrape_page(
        scraper_class, url: str, semaphore: asyncio.Semaphore, page_num: int, **kwargs
    ) -> Optional[List[dict]]:
        """
        Scrape una página individual con su propia instancia de browser.

        Args:
            scraper_class: Clase del scraper a instanciar
            url: URL a scrapear
            semaphore: Semáforo para limitar browsers concurrentes
            page_num: Número de página para logging
            **kwargs: Argumentos adicionales para el scraper

        Returns:
            Lista de ofertas o None si falló
        """
        async with semaphore:
            try:
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    scraper = scraper_class(url=url, crawler=crawler, **kwargs)
                    print(f"Starting scrape of page {page_num}: {url}")

                    # Verificar si la página existe antes de scrapear
                    if page_num > 1 and not await scraper.is_next_page_available():
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

    @classmethod
    async def main_scraper(
        cls,
        scraper_class,
        base_job_url: str,
        url_pattern: str,
        max_pages: int = 100,
        max_concurrent_browsers: int = 3,
        **kwargs,
    ):
        """
        Scraper principal con ejecución concurrente.

        Args:
            scraper_class: Clase del scraper específico
            base_job_url: URL base para la primera página
            url_pattern: Patrón de URL para páginas adicionales (debe incluir {page_num})
            max_pages: Número máximo de páginas a scrapear
            max_concurrent_browsers: Máximo de browsers concurrentes
            **kwargs: Argumentos adicionales para el scraper
        """
        # Create dummy instance to get service name
        async with AsyncWebCrawler(config=browser_config) as temp_crawler:
            temp_scraper = scraper_class(url="", crawler=temp_crawler, **kwargs)
            service_name = temp_scraper.service_name

        print(
            f"Starting async {service_name} scraper with max {max_concurrent_browsers} concurrent browsers"
        )

        # Crear semáforo para limitar browsers concurrentes
        semaphore = asyncio.Semaphore(max_concurrent_browsers)

        # Preparar tareas para ejecución concurrente
        tasks = []

        # Primera página (URL base)
        tasks.append(
            cls.scrape_page(scraper_class, base_job_url, semaphore, 1, **kwargs)
        )

        # Páginas adicionales
        for page_num in range(2, max_pages + 1):
            page_url = url_pattern.format(page_num=page_num)
            tasks.append(
                cls.scrape_page(scraper_class, page_url, semaphore, page_num, **kwargs)
            )

        # Ejecutar todas las tareas concurrentemente
        print(f"Launching {len(tasks)} concurrent scraping tasks...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Procesar resultados
        all_offers = []
        successful_pages = 0

        for i, result in enumerate(results):
            page_num = i + 1

            if isinstance(result, Exception):
                print(f"Page {page_num} failed with exception: {result}")
            elif result is None:
                print(f"Page {page_num} returned None (likely no more pages)")
                # Detener procesamiento cuando llegamos a None
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

        # Guardar todas las ofertas en un archivo JSON
        current_time = datetime.now().strftime("%Y%m%d_%H_00")
        file_name = DATA_PATH / f"{service_name}_job_offers_{current_time}.json"

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(all_offers, f, indent=4, ensure_ascii=False)

        print(f"Results saved to: {file_name}")
        print(f"Total offers scraped: {len(all_offers)}")
