"""OASIS HTTP client for fetching from Canada's NOC website."""

import requests
from typing import Optional
from src.config import OASIS_BASE_URL, OASIS_VERSION, REQUEST_TIMEOUT, USER_AGENT


class OASISScraper:
    """HTTP client for fetching HTML from OASIS endpoints."""

    def __init__(self, timeout: Optional[int] = None):
        """Initialize scraper with session and headers.

        Args:
            timeout: Request timeout in seconds (defaults to config.REQUEST_TIMEOUT)
        """
        self.timeout = timeout if timeout is not None else REQUEST_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT
        })

    def search(self, query: str, search_type: str = "Keyword", version: Optional[str] = None) -> str:
        """Fetch search results HTML from OASIS.

        Args:
            query: Search query string
            search_type: Search type - "Keyword" or "Code" (defaults to "Keyword")
            version: OASIS version (defaults to config.OASIS_VERSION)

        Returns:
            Raw HTML response text

        Raises:
            requests.HTTPError: If request fails
        """
        if version is None:
            version = OASIS_VERSION

        url = f"{OASIS_BASE_URL}/OaSIS/OaSISSearchResult"
        params = {
            "searchType": search_type,
            "searchText": query,
            "version": version
        }

        response = self.session.get(url, params=params, timeout=self.timeout, verify=False)
        response.raise_for_status()
        return response.text

    def fetch_profile(self, code: str, version: Optional[str] = None) -> str:
        """Fetch full profile HTML from OASIS.

        Args:
            code: NOC code (e.g., "21232.00")
            version: OASIS version (defaults to config.OASIS_VERSION)

        Returns:
            Raw HTML response text

        Raises:
            requests.HTTPError: If request fails
        """
        if version is None:
            version = OASIS_VERSION

        url = f"{OASIS_BASE_URL}/OASIS/OASISOccProfile"
        # OASIS now requires the .00 suffix (e.g., "21231.00" not "21231")
        if "." not in code:
            code = f"{code}.00"
        params = {
            "code": code,
            "version": version
        }

        response = self.session.get(url, params=params, timeout=self.timeout, verify=False)
        response.raise_for_status()
        return response.text


# Module-level singleton for easy import
scraper = OASISScraper()
