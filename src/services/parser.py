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
            title = text.replace(noc_code, '').strip(' -–')

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
            'title': self._extract_profile_title(soup),
            'main_duties': self._extract_section_list(soup, 'Main duties'),
            'work_activities': self._extract_rating_items(soup, 'Work Activities'),
            'skills': self._extract_rating_items(soup, 'Skills'),
            'abilities': self._extract_rating_items(soup, 'Abilities'),
            'knowledge': self._extract_rating_items(soup, 'Knowledge') or self._extract_rating_items(soup, 'General Learning'),
            'work_context': self._extract_work_context(soup),
            'employment_requirements': self._extract_section_list(soup, 'Employment requirements'),
        }

    def _extract_profile_title(self, soup: BeautifulSoup) -> str:
        """Extract profile title from HTML (first h2 after h1).

        Args:
            soup: BeautifulSoup instance

        Returns:
            Title text or empty string
        """
        # The profile title is in h2.h1 after the page title
        h2 = soup.select_one('h2.h1')
        if h2:
            return h2.get_text(strip=True)

        # Fallback to h1
        h1 = soup.select_one('h1')
        return h1.get_text(strip=True) if h1 else ""

    def _extract_section_list(self, soup: BeautifulSoup, section_name: str) -> List[str]:
        """Extract list items from a section identified by h3 header.

        Args:
            soup: BeautifulSoup instance
            section_name: Name of section header (e.g., 'Main duties')

        Returns:
            List of text content strings
        """
        # Find h3 with the section name
        h3 = soup.find('h3', string=section_name)
        if not h3:
            return []

        # Navigate to panel body and find li elements
        panel_heading = h3.find_parent('div', class_='panel-heading')
        if not panel_heading:
            return []

        panel = panel_heading.find_parent('div', class_='panel')
        if not panel:
            return []

        panel_body = panel.find('div', class_='panel-body')
        if not panel_body:
            return []

        items = [li.get_text(strip=True) for li in panel_body.find_all('li')]
        return [item for item in items if item]

    def _extract_rating_items(self, soup: BeautifulSoup, section_name: str) -> List[str]:
        """Extract items from a rating-based section (Skills, Abilities, etc).

        Args:
            soup: BeautifulSoup instance
            section_name: Name of section header

        Returns:
            List of item names (not the ratings)
        """
        # Find h3 with the section name
        h3 = soup.find('h3', string=section_name)
        if not h3:
            # Try partial match
            h3 = soup.find('h3', string=lambda x: x and section_name in x)
        if not h3:
            return []

        # Navigate to panel body
        panel_heading = h3.find_parent('div', class_='panel-heading')
        if not panel_heading:
            return []

        panel = panel_heading.find_parent('div', class_='panel')
        if not panel:
            return []

        panel_body = panel.find('div', class_='panel-body')
        if not panel_body:
            return []

        # Extract items from rating cells (first cell in each row is the name)
        items = []
        rows = panel_body.select('.wb-eqht-grd')
        for row in rows:
            cells = row.select('.OasisdescriptorRatingCell')
            if cells:
                first_cell = cells[0]
                # Skip if it's a rating cell (has circle icons)
                if first_cell.find('span', class_='scale-option-circle'):
                    continue
                text = first_cell.get_text(strip=True)
                # Skip header cells
                if text and 'Proficiency' not in text and 'level' not in text and 'Importance' not in text:
                    items.append(text)

        return items

    def _extract_work_context(self, soup: BeautifulSoup) -> List[str]:
        """Extract work context items from Work Context section.

        Work Context has a different structure with col-xs-6 divs.

        Args:
            soup: BeautifulSoup instance

        Returns:
            List of work context descriptions
        """
        items = []

        # Find Work Context h3
        h3 = soup.find('h3', string='Work Context')
        if not h3:
            return items

        # Navigate to panel body
        panel_heading = h3.find_parent('div', class_='panel-heading')
        if not panel_heading:
            return items

        panel = panel_heading.find_parent('div', class_='panel')
        if not panel:
            return items

        panel_body = panel.find('div', class_='panel-body')
        if not panel_body:
            return items

        # Work context uses Descriptors-Rating-By-MeasuredDimension-Div with col-xs-6 cells
        for div in panel_body.select('.Descriptors-Rating-By-MeasuredDimension-Div'):
            # Find the first col-xs-6 cell which contains the dimension name
            cells = div.select('.col-xs-6.pad10')
            if cells:
                first_cell = cells[0]
                # Skip if it contains rating circles
                if first_cell.find('span', class_='scale-option-circle'):
                    continue
                text = first_cell.get_text(strip=True)
                if text and text not in items:  # Avoid duplicates
                    items.append(text)

        return items


# Module-level singleton for easy import
parser = OASISParser()
