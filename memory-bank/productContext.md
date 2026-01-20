# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.

2026-01-20 22:48:38 - Initial Memory Bank creation based on project analysis.

## Project Goal

General Crawler is a sophisticated job scraping system designed to extract job offers from multiple Mexican job sites asynchronously and concurrently. The system uses [`crawl4ai`](src/config.py:4) for high-performance web scraping with controlled browser concurrency through semaphores.

## Key Features

* **Asynchronous Scraping**: Utilizes [`crawl4ai`](src/job/mixins.py:17) for high-performance web crawling
* **Controlled Concurrency**: Semaphore system to limit simultaneous browsers and prevent resource overload
* **Modular Architecture**: Mixin-based system for code reuse between scrapers through [`BaseScraperSetup`](src/job/mixins.py:23), [`AsyncScraperMixin`](src/job/mixins.py:72), and [`ConcurrentScraperMixin`](src/job/mixins.py:185)
* **Intelligent Data Extraction**: Comprehensive job details extraction including titles, companies, locations, descriptions, requirements, and salaries
* **JSON Storage**: Structured data output with timestamped results in [`DATA_PATH`](src/config.py:7)
* **Multi-site Support**: Currently supports OCC.com.mx and ComputTrabajo.com with extensible architecture

## Overall Architecture

The system follows a hierarchical mixin pattern:

1. **Base Layer**: [`BaseScraperSetup`](src/job/mixins.py:23) - Abstract interface defining common scraper properties
2. **Async Layer**: [`AsyncScraperMixin`](src/job/mixins.py:72) - Shared asynchronous functionality for page processing
3. **Concurrent Layer**: [`ConcurrentScraperMixin`](src/job/mixins.py:185) - Semaphore-based concurrent execution
4. **Implementation Layer**: Site-specific scrapers ([`src/job/occ/scraper.py`](src/job/occ/scraper.py), [`src/job/compu_trabajo/scraper.py`](src/job/compu_trabajo/scraper.py))

The architecture supports 48-51% code reduction compared to the original implementation while enabling true concurrent scraping across multiple browser instances.