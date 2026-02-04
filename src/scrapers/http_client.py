"""Rate-limited HTTP client for TBS scraping.

Provides a session-based HTTP client with automatic retry logic
and rate limiting to respect government servers.
"""

import time
from typing import Dict, Any, Tuple, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# TBS URLs
TBS_BASE_URL = "https://www.canada.ca"
OCCUPATIONAL_GROUPS_PATH = "/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html"
DEFINITIONS_PATH = "/en/treasury-board-secretariat/services/collective-agreements/occupational-groups/definitions.html"
ALLOCATION_GUIDE_PATH = "/en/treasury-board-secretariat/services/classification/job-evaluation/guide-allocating-positions-using-occupational-group-definitions.html"

# Request configuration
RATE_LIMIT_DELAY = 1.0  # seconds between requests (user decision in CONTEXT.md)
REQUEST_TIMEOUT = 30  # seconds


def create_scraping_session() -> requests.Session:
    """Create a requests session with retry logic.

    Configures HTTPAdapter with Retry strategy for automatic
    retry on 429 (rate limit) and 5xx (server errors) with
    exponential backoff.

    Returns:
        Configured requests.Session with retry adapter
    """
    session = requests.Session()

    # Retry on transient errors with exponential backoff
    # Wait 2, 4, 8 seconds between retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Set User-Agent for transparency (IETF best practice)
    session.headers.update({
        "User-Agent": "JD-Builder/1.0 (TBS Occupational Data Scraper)"
    })

    return session


class TBSHttpClient:
    """Rate-limited HTTP client for TBS government pages.

    Ensures polite scraping with 1 request/second rate limiting
    and automatic retry on transient errors.

    Example:
        client = TBSHttpClient()
        content, meta = client.fetch_occupational_groups_table()
        print(f"Fetched {len(content)} bytes, status {meta['status']}")
    """

    def __init__(self, session: Optional[requests.Session] = None):
        """Initialize the HTTP client.

        Args:
            session: Optional pre-configured session. If None,
                creates one with default retry configuration.
        """
        self.session = session if session else create_scraping_session()
        self._last_request_time: Optional[float] = None

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests.

        Sleeps if less than RATE_LIMIT_DELAY seconds have passed
        since the last request.
        """
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < RATE_LIMIT_DELAY:
                sleep_time = RATE_LIMIT_DELAY - elapsed
                time.sleep(sleep_time)
        self._last_request_time = time.time()

    def fetch(self, url: str) -> Tuple[bytes, Dict[str, Any]]:
        """Fetch a URL with rate limiting.

        Makes a GET request with timeout, respecting rate limits.
        Raises HTTPError on failure (after retries exhausted).

        Args:
            url: Full URL to fetch

        Returns:
            Tuple of (response.content, response_metadata)
            where response_metadata contains:
                - url: Final URL (after redirects)
                - status: HTTP status code
                - headers: Dict of response headers
                - elapsed_ms: Request duration in milliseconds

        Raises:
            requests.HTTPError: If request fails after retries
        """
        self._rate_limit()

        response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        metadata = {
            "url": response.url,
            "status": response.status_code,
            "headers": dict(response.headers),
            "elapsed_ms": response.elapsed.total_seconds() * 1000,
        }

        return response.content, metadata

    def fetch_occupational_groups_table(self) -> Tuple[bytes, Dict[str, Any]]:
        """Fetch the TBS occupational groups concordance table.

        Returns:
            Tuple of (html_content, metadata)
        """
        url = TBS_BASE_URL + OCCUPATIONAL_GROUPS_PATH
        return self.fetch(url)

    def fetch_definitions_page(self) -> Tuple[bytes, Dict[str, Any]]:
        """Fetch the TBS occupational group definitions page.

        Returns:
            Tuple of (html_content, metadata)
        """
        url = TBS_BASE_URL + DEFINITIONS_PATH
        return self.fetch(url)

    def fetch_definition_anchor(self, anchor: str) -> Tuple[bytes, Dict[str, Any]]:
        """Fetch the definitions page for a specific group anchor.

        Note: Full page is fetched; anchor is for parsing context.
        The anchor should be like '#def-ai' or just 'def-ai'.

        Args:
            anchor: Group anchor (e.g., '#def-ai' or 'def-ai')

        Returns:
            Tuple of (html_content, metadata)
        """
        # Remove leading # if present
        if anchor.startswith("#"):
            anchor = anchor[1:]
        url = f"{TBS_BASE_URL}{DEFINITIONS_PATH}#{anchor}"
        return self.fetch(url)

    def fetch_allocation_guide(self) -> Tuple[bytes, Dict[str, Any]]:
        """Fetch the TBS allocation guide page.

        Returns:
            Tuple of (html_content, metadata)
        """
        url = TBS_BASE_URL + ALLOCATION_GUIDE_PATH
        return self.fetch(url)
