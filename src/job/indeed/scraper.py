# /// script
# requires-python = ">=3.13"
# dependencies = [
#      "beautifulsoup4",
#      "httpx",
#      "random", # Added for random delays
#      "time",   # Added for random delays
# ]
# ///

from __future__ import annotations

import random
import time
from collections.abc import Generator

import httpx
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
# Base URL for Indeed job search (using the Mexican domain as an example)
INDEED_BASE_URL = "https://www.indeed.com.mx/jobs?"
# Indeed uses a 'start' parameter for pagination, where results are 10 per page.
RESULTS_PER_PAGE = 10
# Safety limit to prevent accidental infinite loops/excessive requests
MAX_PAGES = 5

# Crucial upgrade: Mimic a real web browser to avoid immediate blocking.
# This set of headers is vital for a robust, stealthy scraping effort.
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "https://www.google.com/",  # Fakes a referrer link
}
# ---------------------


def fetch_jobs(job_title: str, location: str) -> Generator[tuple[str, str, str]]:
    """
    Fetches job listings from Indeed, handling pagination and mimicking human behavior.

    Args:
        job_title: The keyword search term (e.g., "Data Scientist").
        location: The location to search in (e.g., "Bangalore").

    Yields:
        A tuple containing the job title, company name, and location of a job listing.
    """
    # URL-encode the search terms
    q_encoded = job_title.replace(" ", "+")
    l_encoded = location.replace(" ", "+")

    current_offset = 0
    total_jobs_scraped = 0

    # Loop to handle pagination using the 'start' parameter
    for page_num in range(MAX_PAGES):
        search_url = (
            f"{INDEED_BASE_URL}q={q_encoded}&l={l_encoded}&start={current_offset}"
        )

        print(
            f"\n--- Page {page_num + 1} | Offset {current_offset} | URL: {search_url} ---"
        )

        # Implement polite scraping delay (REQUIRED for production)
        if page_num > 0:
            delay = random.uniform(2.0, 5.0)
            print(f"Waiting for {delay:.2f} seconds to avoid rate limiting...")
            time.sleep(delay)

        try:
            # Send request with custom headers
            response = httpx.get(search_url, headers=DEFAULT_HEADERS, timeout=10)
            response.raise_for_status()
        except httpx.HTTPError as e:
            # Handle HTTP errors (e.g., 404, 429 Too Many Requests)
            print(f"HTTP Error fetching data on page {page_num + 1}: {e}")
            break
        except Exception as e:
            # Catch other connection errors (e.g., DNS resolution, timeouts)
            print(f"An unexpected error occurred: {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        # Resilient Selector: Targets the general job card structure
        job_cards = soup.find_all(
            "div",
            class_=lambda x: x
            and ("jobsearch-SerpJobCard" in x or "job_list_item" in x),
        )

        jobs_on_page = 0

        for job in job_cards:
            try:
                # Extract job title
                title_tag = job.find("a", attrs={"data-tn-element": "jobTitle"})
                job_title_text = title_tag.text.strip() if title_tag else "N/A"

                # Extract company name
                company_tag = job.find("span", {"class": "company"})
                company_name = company_tag.text.strip() if company_tag else "N/A"

                # Extract location
                location_tag = job.find("div", {"class": "location"}) or job.find(
                    "span", {"class": "location"}
                )
                job_location = (
                    location_tag.text.strip() if location_tag else location
                )  # Use search location as fallback

                if job_title_text != "N/A" and company_name != "N/A":
                    yield job_title_text, company_name, job_location
                    jobs_on_page += 1
                    total_jobs_scraped += 1

            except AttributeError:
                # Safely skip corrupted or malformed entries
                continue

        # Logic for stopping pagination: If we didn't find any jobs, we've hit the end.
        if jobs_on_page == 0 or jobs_on_page < RESULTS_PER_PAGE:
            print(
                f"Finished scraping: Found {jobs_on_page} results on this page, indicating end of listings or max pages reached."
            )
            break

        # Prepare for the next page
        current_offset += RESULTS_PER_PAGE

    print(
        f"\n[SUMMARY] Successfully scraped {total_jobs_scraped} jobs over {page_num + 1} pages."
    )


if __name__ == "__main__":
    # --- Customize your search here ---
    TITLE = "Python Developer"
    LOCATION = "Remote"

    print(f"--- STARTING ROBUST SCRAPE FOR: {TITLE} in {LOCATION} ---")

    jobs_found = list(fetch_jobs(TITLE, LOCATION))

    print("\n--- FINAL RESULTS (Top 50 Jobs) ---")
    if jobs_found:
        for i, job in enumerate(jobs_found, 1):
            title, company, loc = job
            print(f"Job {i:>3}: {title} at {company} ({loc})")
    else:
        print("No jobs found or an error occurred. Check the logs above.")
