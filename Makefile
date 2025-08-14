.PHONY: install_firefox_driver


install_firefox_driver:
	@echo "Installing geckodriver for Firefox..."
	playwright install firefox

format:
	@echo "Formatting code..."
	uv run ruff check --fix .