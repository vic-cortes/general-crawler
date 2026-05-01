# General Crawler - Job Scrapers

Sistema de scrapers asíncronos y concurrentes para extraer ofertas de trabajo de múltiples sitios web mexicanos.

## Características

- Scraping asíncrono con `crawl4ai` (OCC, CompuTrabajo) y `httpx` (Indeed)
- Concurrencia controlada por semáforos para limitar browsers simultáneos
- Arquitectura de mixins para reutilizar lógica entre scrapers
- Extracción de detalles completos por oferta (salario, requisitos, URL directa)
- Resultados guardados en `data/` como JSON con timestamp

## Uso rápido

```bash
# Instalar dependencias
uv sync
make install_firefox_driver   # solo la primera vez

# Correr un scraper directamente
uv run python src/job/occ/scraper.py
uv run python src/job/compu_trabajo/scraper.py
uv run python src/job/indeed/scraper.py

# Correr desde código
import asyncio
from src.job.occ.scraper import OCCConcurrentScraper

asyncio.run(OCCConcurrentScraper.run(max_pages=50, max_concurrent_browsers=5))
```

## Scrapers disponibles

| Scraper | URL base | Paginación | Tecnología |
|---|---|---|---|
| OCC | `occ.com.mx/empleos/de-python/` | `?page={n}` | crawl4ai + BeautifulSoup |
| CompuTrabajo | `mx.computrabajo.com/empleos-en-acuna` | `?p={n}` | crawl4ai + BeautifulSoup |
| Indeed | `indeed.com.mx/jobs` | `?start={offset}` | httpx + BeautifulSoup |

> **Nota:** Indeed usa `httpx` con headers que imitan un navegador real (sin browser automation) ya que su estructura no requiere JS.

## Arquitectura

Los scrapers de `crawl4ai` siguen una jerarquía de clases definida en `src/job/mixins.py`:

```
BaseScraperSetup  →  define interfaz: service_name, base_selector, _output_schema()
AsyncScraperMixin →  _get_overview(), _get_details(), get_data()
BaseScraper       →  dataclass que combina ambos (recibe url + crawler)
ConcurrentScraperMixin → scrape_page() + main_scraper() con semáforos
```

Flujo de datos:
1. `main_scraper()` lanza N browsers concurrentes (controlado por `asyncio.Semaphore`)
2. `_get_overview()` extrae el listado usando `JsonCssExtractionStrategy` (CSS → JSON)
3. `_get_details()` hace click en cada oferta y parsea el panel de detalle con BeautifulSoup
4. El resultado se guarda en `data/<service_name>_job_offers_<YYYYMMDD_HH_00>.json`

### Campos de salida por oferta

| Campo | Origen |
|---|---|
| `title`, `company`, `location`, `relative_date`, `description` | Vista de listado (CSS extraction) |
| `details.description`, `details.requirements`, `details.salary`, `details.job_url` | Vista de detalle (BeautifulSoup) |
| `offer_id`, `current_datetime` | Vista de detalle |

## Desarrollo

```bash
uv run pytest                                          # todos los tests
uv run pytest test/test_utils.py::test_function_name  # test específico
uv run ruff check --fix .                              # format + lint
```

### Agregar un nuevo scraper

1. Crear `src/job/<board>/scraper.py` con una clase que herede de `BaseScraper`
2. Implementar las propiedades abstractas: `service_name`, `base_selector`, `key_css_selector`, `_output_schema()`
3. Implementar los métodos: `get_job_details()`, `_get_offer_id()`, `is_next_page_available()`
4. Crear una clase `<Board>ConcurrentScraper(ConcurrentScraperMixin)` con un método `run()`

```python
from src.job.mixins import BaseScraper, ConcurrentScraperMixin

class NuevoScraper(BaseScraper):
    @property
    def service_name(self) -> str:
        return "nuevo_sitio"
    # ...implementar resto de métodos

class NuevoConcurrentScraper(ConcurrentScraperMixin):
    @classmethod
    async def run(cls, max_pages: int = 100, max_concurrent_browsers: int = 3):
        await cls.main_scraper(
            scraper_class=NuevoScraper,
            base_job_url="https://sitio.com/empleos",
            url_pattern="https://sitio.com/empleos?page={page_num}",
            max_pages=max_pages,
            max_concurrent_browsers=max_concurrent_browsers,
        )
```

## Docker

```bash
docker build -t general-crawler .

docker-compose run occ-scraper
docker-compose run indeed-scraper
docker-compose run compu-trabajo-scraper
docker-compose --profile test up test
```

Variables de entorno del contenedor: `HEADLESS=true`, `LOG_LEVEL=INFO`, `PYTHONPATH=/app`
