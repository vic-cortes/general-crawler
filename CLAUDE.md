# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python-based web crawler for scraping job listings from multiple job boards (OCC, CompuTrabajo, Indeed). Uses `crawl4ai` as the async browser automation framework with CSS-based structured extraction.

## Development Commands

```bash
uv sync                          # Install dependencies
make install_firefox_driver      # Install Playwright Firefox driver (if needed)
uv run pytest                    # Run all tests
uv run pytest test/test_utils.py::test_function_name  # Single test
uv run ruff check --fix .        # Format and lint
uv run python src/job/occ/scraper.py  # Run a scraper directly
```

## Scraper Architecture

Each job board lives in its own package under `src/job/<board>/scraper.py`. The class hierarchy is:

```
BaseScraperSetup (ABC)   — defines abstract properties: service_name, base_selector, key_css_selector, _output_schema()
AsyncScraperMixin        — provides _get_overview(), _get_details(), get_data()
BaseScraper (dataclass)  — combines both; takes url + crawler as constructor args
ConcurrentScraperMixin   — adds scrape_page() + main_scraper() for multi-browser parallel runs
```

To add a new job board:
1. Create `src/job/<board>/scraper.py` with a class extending `BaseScraper`
2. Implement all abstract properties and `get_job_details()`, `_get_offer_id()`, `is_next_page_available()`
3. Add a `ConcurrentScraper` class extending `ConcurrentScraperMixin` with a `run()` classmethod

### Data flow
1. `ConcurrentScraperMixin.main_scraper()` spawns N concurrent browsers via `asyncio.Semaphore`
2. Each browser calls `_get_overview()` using `JsonCssExtractionStrategy` (CSS-driven JSON extraction)
3. For each overview item, `_get_details()` clicks the listing and parses the detail panel with BeautifulSoup
4. Results are saved as `data/<service_name>_job_offers_<YYYYMMDD_HH_00>.json`

### Key files
- `src/config.py` — `BrowserConfig` (Chromium, headless) and `DATA_PATH`
- `src/job/mixins.py` — all base/mixin classes
- `src/utils.py` — `DateConverter` for Spanish relative dates ("hace 2 días", "ayer", month names)
- `src/job/common/` — shared constants and utilities

### Output schema fields
Each scraper defines its own `_output_schema()` returning a `JsonCssExtractionStrategy`-compatible dict. Standard fields across boards: `title`, `company`, `location`, `relative_date`, `description`. Detail fields (added by `get_job_details()`): `job_url`, `salary`, `requirements`, `offer_id`, `current_datetime`.
