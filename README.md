# General Crawler - Job Scrapers

Un sistema de scrapers asíncronos y concurrentes para extraer ofertas de trabajo de múltiples sitios web mexicanos.

## 🚀 Características

- **Scraping Asíncrono**: Utiliza `crawl4ai` para scraping web de alto rendimiento
- **Concurrencia Controlada**: Sistema de semáforos para limitar browsers simultáneos
- **Arquitectura Modular**: Sistema de mixins para reutilizar código entre scrapers
- **Extracción Inteligente**: Obtiene detalles completos de cada oferta de trabajo
- **Almacenamiento JSON**: Guarda resultados en formato JSON estructurado

## 📁 Estructura del Proyecto

```
src/job/
├── mixins.py                 # Clases base y mixins compartidos
├── occ/
│   └── scraper.py           # Scraper para OCC.com.mx
├── compu_trabajo/
│   └── scraper.py           # Scraper para ComputTrabajo.com
└── common/
    ├── constants.py         # Constantes compartidas
    └── utils.py             # Utilidades comunes
```

## 🏗️ Arquitectura

### Sistema de Mixins

El proyecto utiliza un sistema de mixins para compartir funcionalidad común entre scrapers:

#### [`BaseScraperSetup`](src/job/mixins.py)
Clase abstracta que define la interfaz común para todos los scrapers:
- `service_name`: Nombre del servicio
- `base_selector`: Selector CSS para ofertas
- `key_css_selector`: Selector para esperar carga de página
- `_output_schema()`: Esquema de extracción de datos

#### [`AsyncScraperMixin`](src/job/mixins.py)
Proporciona funcionalidad asíncrona compartida:
- `_get_overview()`: Extrae listado de ofertas
- `_get_details()`: Obtiene detalles individuales
- `get_data()`: Método principal de scraping
- `is_next_page_available()`: Verifica páginas disponibles

#### [`BaseScraper`](src/job/mixins.py)
Combina configuración base y funcionalidad asíncrona:
- Manejo de sesiones únicas por crawler
- Configuración de crawling estándar

#### [`ConcurrentScraperMixin`](src/job/mixins.py)
Implementa scraping concurrente con semáforos:
- `scrape_page()`: Scraping de página individual
- `main_scraper()`: Coordinador de scraping concurrente
- Control de recursos con semáforos

### Scrapers Específicos

#### OCC Scraper ([`src/job/occ/scraper.py`](src/job/occ/scraper.py))
- **URL Base**: `https://www.occ.com.mx/empleos/de-python/`
- **Paginación**: `?page={num}`
- **Especialización**: Extracción de salarios, requisitos y descripciones específicas de OCC

#### ComputTrabajo Scraper ([`src/job/compu_trabajo/scraper.py`](src/job/compu_trabajo/scraper.py))
- **URL Base**: `https://mx.computrabajo.com/trabajo-de-python`
- **Paginación**: `?p={num}`
- **Especialización**: Manejo de estructura específica de ComputTrabajo

## ⚡ Uso

### Ejecución Básica

```python
# OCC Scraper
python src/job/occ/scraper.py

# ComputTrabajo Scraper
python src/job/compu_trabajo/scraper.py
```

### Ejecución Programática

```python
import asyncio
from src.job.occ.scraper import OCCConcurrentScraper
from src.job.compu_trabajo.scraper import ComputTrabajoConcurrentScraper

# OCC con parámetros personalizados
await OCCConcurrentScraper.run(
    max_pages=50,
    max_concurrent_browsers=5
)

# ComputTrabajo
await ComputTrabajoConcurrentScraper.run(
    max_pages=100,
    max_concurrent_browsers=3
)
```

## 🔧 Configuración

### Parámetros de Concurrencia

- **`max_pages`**: Número máximo de páginas a scrapear (default: 100)
- **`max_concurrent_browsers`**: Máximo de browsers simultáneos (default: 3)

### Configuración de Browser

La configuración del browser se define en [`src/config.py`](src/config.py) mediante `browser_config`.

## 📊 Datos Extraídos

Cada oferta incluye:

### Datos Básicos
- `title`: Título del puesto
- `company`: Nombre de la empresa
- `location`: Ubicación del trabajo
- `relative_date`: Fecha de publicación
- `description`: Descripción breve

### Detalles Completos
- `details.description`: Descripción completa
- `details.requirements`: Requisitos del puesto
- `details.salary`: Información salarial (cuando disponible)
- `details.job_url`: URL directa a la oferta
- `offer_id`: ID único de la oferta
- `current_datetime`: Timestamp de extracción

## 📈 Mejoras de Rendimiento

### Antes de la Refactorización
- Scraping secuencial página por página
- Una sola instancia de browser
- ~360 líneas de código duplicado

### Después de la Refactorización
- **Concurrencia Real**: Múltiples browsers trabajando simultáneamente
- **Reducción de Código**: 48-51% menos líneas por scraper
- **Arquitectura Modular**: Sistema de herencia y mixins
- **Control de Recursos**: Semáforos para evitar sobrecarga

## 🛠️ Desarrollo

### Agregar un Nuevo Scraper

1. Heredar de [`BaseScraper`](src/job/mixins.py):

```python
from src.job.mixins import BaseScraper, ConcurrentScraperMixin

class NuevoScraper(BaseScraper):
    @property
    def service_name(self) -> str:
        return "nuevo_sitio"
    
    @property
    def base_selector(self) -> str:
        return "div.job-offer"
    
    # Implementar métodos requeridos...
```

2. Crear clase concurrente:

```python
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

### Dependencias

- `crawl4ai`: Web crawler asíncrono
- `beautifulsoup4`: Parsing HTML
- `asyncio`: Programación asíncrona

## 📝 Logs y Debugging

El sistema proporciona logging detallado:

```
Starting async occ scraper with max 3 concurrent browsers
Launching 100 concurrent scraping tasks...
Starting scrape of page 1: https://www.occ.com.mx/empleos/de-python/
Starting scrape of page 2: https://www.occ.com.mx/empleos/de-python/?page=2
...
Completed page 1: found 25 offers
Completed page 2: found 23 offers
...
Scraping completed. Processed 45 pages, found 1,125 total offers
Results saved to: data/occ_job_offers_20260117_13_00.json
Total offers scraped: 1,125
```

## 🐳 Docker

### Construcción y Ejecución

```bash
# Construir la imagen
docker build -t general-crawler .

# Ejecutar todos los scrapers
docker-compose up

# Ejecutar un scraper específico
docker-compose run occ-scraper
docker-compose run indeed-scraper
docker-compose run compu-trabajo-scraper

# Ejecutar pruebas
docker-compose --profile test up test
```

### Servicios Disponibles

- **scrapers**: Servicio base con entorno configurado
- **occ-scraper**: Scraper específico para OCC.com.mx
- **indeed-scraper**: Scraper específico para Indeed
- **compu-trabajo-scraper**: Scraper específico para ComputTrabajo
- **test**: Servicio para ejecutar pruebas unitarias

### Variables de Entorno

- `HEADLESS=true`: Ejecutar browser en modo headless
- `LOG_LEVEL=INFO`: Nivel de logging
- `PYTHONPATH=/app`: Path de Python en contenedor

### Volúmenes

- `./results:/app/results`: Almacenamiento de resultados
- `./src:/app/src`: Código fuente para desarrollo

## 🚦 Estado del Proyecto

- ✅ Sistema de mixins implementado
- ✅ Scraping asíncrono y concurrente
- ✅ Control de recursos con semáforos
- ✅ Scrapers OCC y ComputTrabajo refactorizados
- ✅ Extracción de detalles completos
- ✅ Almacenamiento en JSON
- ✅ Soporte Docker completo

## 📄 Licencia

Este proyecto es de uso interno y educativo.