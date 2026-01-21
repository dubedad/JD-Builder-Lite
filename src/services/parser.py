"""OASIS HTML parser using BeautifulSoup."""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from src.models.noc import SearchResult
from src.utils.selectors import get_selector, get_fallback


class OASISParser:
    """HTML parser for extracting structured data from OASIS pages."""

    # Regex pattern to match NOC codes like "21232" or "21232.00"
    NOC_CODE_PATTERN = re.compile(r'\d{5}(?:\.\d{2})?')

    def parse_search_results(self, html: str) -> List[SearchResult]:
        """Parse search results HTML into SearchResult models.

        Args:
            html: Raw HTML from OASIS search page

        Returns:
            List of SearchResult models with NOC code, title, and URL
        """
        soup = BeautifulSoup(html, 'lxml')
        results = []

        # Try primary selector, then fallback
        primary = get_selector("search_results")
        elements = soup.select(primary)

        if not elements:
            fallback = get_fallback("search_results")
            elements = soup.select(fallback)

        for element in elements:
            # Find link element
            link_primary = get_selector("result_link")
            link = element.select_one(link_primary)

            if not link:
                link_fallback = get_fallback("result_link")
                link = element.select_one(link_fallback)

            if not link:
                continue

            # Extract NOC code from link text or URL
            text = link.get_text(strip=True)
            href = link.get('href', '')

            # Try to find code in text first, then in URL
            code_match = self.NOC_CODE_PATTERN.search(text)
            if not code_match:
                code_match = self.NOC_CODE_PATTERN.search(href)

            if not code_match:
                continue  # Skip rows without valid NOC code

            noc_code = code_match.group(0)
            title = text.replace(noc_code, '').strip(' -')

            results.append(SearchResult(
                noc_code=noc_code,
                title=title,
                url=href
            ))

        return results

    def parse_profile(self, html: str, code: str) -> Dict[str, Any]:
        """Parse profile HTML into structured data dict.

        Args:
            html: Raw HTML from OASIS profile page
            code: NOC code for this profile

        Returns:
            Dict with noc_code, title, and all profile sections as lists
        """
        soup = BeautifulSoup(html, 'lxml')

        return {
            'noc_code': code,
            'title': self._extract_title(soup),
            'main_duties': self._extract_list(soup, 'main_duties'),
            'work_activities': self._extract_list(soup, 'work_activities'),
            'skills': self._extract_list(soup, 'skills'),
            'abilities': self._extract_list(soup, 'abilities'),
            'knowledge': self._extract_list(soup, 'knowledge'),
            'work_context': self._extract_list(soup, 'work_context'),
            'employment_requirements': self._extract_list(soup, 'employment_requirements'),
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract profile title from HTML.

        Args:
            soup: BeautifulSoup instance

        Returns:
            Title text or empty string
        """
        primary = get_selector("profile_title")
        element = soup.select_one(primary)

        if not element:
            fallback = get_fallback("profile_title")
            element = soup.select_one(fallback)

        return element.get_text(strip=True) if element else ""

    def _extract_list(self, soup: BeautifulSoup, element_name: str) -> List[str]:
        """Extract list of items from HTML section.

        Args:
            soup: BeautifulSoup instance
            element_name: Name of element in selectors (e.g., 'main_duties')

        Returns:
            List of text content strings, filtered for empty strings
        """
        primary = get_selector(element_name)
        elements = soup.select(primary)

        if not elements:
            fallback = get_fallback(element_name)
            elements = soup.select(fallback)

        # Extract text and filter out empty strings
        items = [elem.get_text(strip=True) for elem in elements]
        return [item for item in items if item]


# Module-level singleton for easy import
parser = OASISParser()
