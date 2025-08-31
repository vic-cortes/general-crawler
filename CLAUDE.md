# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based general web crawler focused on job scraping from multiple job boards. The project uses crawl4ai as the core web crawling framework with async support and CSS-based extraction strategies.

## Architecture

- **Main modules**: Located in `src/` with job-specific scrapers in `src/job/`
- **Job scrapers**: Each job board (Indeed, OCC, Computrabajo) has its own module with dedicated scrapers
- **Browser config**: Centralized in `src/config.py` using Firefox with headless mode configurable
- **Data utilities**: Date conversion and parsing utilities in `src/utils.py` for handling Spanish date formats
- **Output**: JSON extraction using CSS selectors with standardized field schemas

## Development Commands

### Setup
- Install Firefox driver for Playwright: `make install_firefox_driver`
- Format code: `make format` (uses ruff)

### Testing
- Run tests: `uv run pytest`
- Run specific test: `uv run pytest test/test_utils.py`

### Linting/Formatting
- Format and fix code: `uv run ruff check --fix .`
- Check code: `uv run ruff check .`

### Running the project
- This project uses `uv` for dependency management
- Run Python scripts with: `uv run python <script>`

## Key Technical Details

### Scraper Architecture
- Each job board scraper extends a base pattern with URL configuration, CSS selectors, and output schemas
- Uses `JsonCssExtractionStrategy` for structured data extraction
- Implements detail page scraping for additional job information
- Date parsing handles relative dates ("hace 2 días") and Spanish month names

### Browser Configuration
- Default browser: Firefox (non-headless mode)
- Browser config centralized in `src/config.py`
- Uses crawl4ai's `BrowserConfig` and `AsyncWebCrawler`

### Data Processing
- `DateConverter` class handles Spanish date formats and relative dates
- Standardized output format across all scrapers
- JSON output with consistent field naming (title, company, location, etc.)