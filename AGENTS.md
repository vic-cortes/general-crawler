# AGENTS.md

This file provides guidance to agentic coding agents working in this repository.

## Project Overview

This is a Python-based general web crawler focused on job scraping from multiple job boards. The project uses crawl4ai as the core web crawling framework with async support and CSS-based extraction strategies.

## Development Commands

### Environment Setup
- Install dependencies: `uv sync`
- Install Firefox driver for Playwright: `make install_firefox_driver`

### Code Quality
- Format and fix code: `make format` or `uv run ruff check --fix .`
- Check code style: `uv run ruff check .`

### Testing
- Run all tests: `uv run pytest`
- Run specific test file: `uv run pytest test/test_utils.py`
- Run specific test function: `uv run pytest test/test_utils.py::test_function_name`
- Run tests with verbose output: `uv run pytest -v`

### Running the Project
- Use `uv run python <script>` for Python scripts
- The project uses `uv` for dependency management

## Code Style Guidelines

### Import Organization
- Standard library imports first, then third-party, then local imports
- Use absolute imports for local modules (e.g., `from src.config import browser_config`)
- Group imports by type with blank lines between groups

### Formatting
- Uses ruff for formatting and linting
- Line length: 88 characters (ruff default)
- Use f-strings for string formatting
- Prefer type hints for all function parameters and return values

### Type Hints
- Use modern type hints: `str | None` instead of `Optional[str]`
- Use `dict`, `list`, `tuple` for generic types
- Use `dataclass` for data containers
- Always type class attributes and method parameters

### Naming Conventions
- Classes: PascalCase (e.g., `DateConverter`, `BaseScraper`)
- Functions and variables: snake_case (e.g., `get_job_details`, `service_name`)
- Constants: UPPER_SNAKE_CASE (e.g., `BASE_URL`, `DEFAULT_FORMAT`)
- Private methods: prefix with underscore (e.g., `_get_digit`)

### Error Handling
- Use specific exceptions when possible
- Include descriptive error messages with context
- Use try-except blocks for web scraping operations
- Log or print errors with relevant context (e.g., page numbers, URLs)

### Async/Await Patterns
- All web scraping operations should be async
- Use `async with` for crawler instances
- Implement proper semaphore usage for concurrent operations
- Use `asyncio.gather()` for concurrent task execution

### Class Design Patterns
- Use mixins for shared functionality (see `src/job/mixins.py`)
- Implement abstract base classes for common interfaces
- Use dataclasses for simple data containers
- Follow the scraper pattern: base class + specific implementations

### Web Scraping Best Practices
- Use CSS selectors for element extraction
- Implement wait strategies for dynamic content
- Handle missing elements gracefully (return None or empty dict)
- Use session IDs for crawler state management
- Implement rate limiting through semaphores

### File Organization
- Main modules in `src/`
- Job-specific scrapers in `src/job/`
- Shared utilities in `src/job/common/`
- Tests in `test/` directory
- Configuration in `src/config.py`

### Documentation
- Use docstrings for all classes and public methods
- Include parameter types and return values in docstrings
- Use Spanish comments for Spanish-specific code (date handling)
- Keep comments concise and relevant

### Data Processing
- Handle Spanish date formats and relative dates
- Use consistent JSON output schemas
- Implement data conversion utilities (DateConverter, SalaryConverter)
- Store results in `data/` directory with timestamped filenames

### Browser Configuration
- Centralized browser config in `src/config.py`
- Default to Firefox with headless mode
- Use crawl4ai's `BrowserConfig` and `AsyncWebCrawler`
- Support for multiple browser types through enum

## Testing Guidelines

### Test Structure
- Place tests in `test/` directory
- Use descriptive test function names
- Test both success and error cases
- Mock external dependencies when appropriate

### Test Data
- Use sample data files for testing parsing logic
- Test with various date formats and edge cases
- Include tests for concurrent operations

## Key Technical Patterns

### Scraper Architecture
- Each job board scraper extends base classes
- Use `JsonCssExtractionStrategy` for structured data extraction
- Implement detail page scraping for additional information
- Handle pagination and concurrent page processing

### Date Handling
- Support Spanish month names and relative dates
- Convert relative dates ("hace 2 días") to absolute dates
- Use consistent date formatting across scrapers

### Concurrent Processing
- Implement semaphore-based rate limiting
- Use async patterns for I/O operations
- Handle exceptions in concurrent contexts gracefully