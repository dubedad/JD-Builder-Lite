"""OASIS HTML parser using BeautifulSoup."""

import re
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from src.models.noc import (
    SearchResult, EnrichedSearchResult, NOCHierarchy, BROAD_CATEGORIES,
    ReferenceAttributes, CareerMobilityPath, Interest, JobRequirements
)
from src.services.csv_loader import TEER_CATEGORIES
from src.utils.selectors import get_selector, get_fallback

logger = logging.getLogger(__name__)


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

    def parse_search_results_enhanced(self, html: str) -> List[EnrichedSearchResult]:
        """Parse search results HTML into EnrichedSearchResult models.

        Extracts available card data from OaSIS search results HTML:
        - NOC code and title from link
        - Lead statement (fa-book icon cell)
        - TEER description (fa-bookmark icon cell)
        - Broad category (fa-truck/fa-pen-alt icon cell)
        - Matching criteria (fa-search icon cell)
        - Minor group (derived from NOC code)

        Note: example_titles, mobility_progression, source_table, publication_date,
        and skills/abilities/knowledge require profile fetch and are left as None.

        Args:
            html: Raw HTML from OASIS search page

        Returns:
            List of EnrichedSearchResult models with available card data
        """
        soup = BeautifulSoup(html, 'lxml')
        results = []

        # OaSIS uses table rows with class 'cardsTr' for each result
        # Each row contains: hidden cols, profile link, BOC, TEER, lead statement, matching
        rows = soup.select('tr.cardsTr, tr.eqht-trgt')

        for row in rows:
            # Skip header rows
            if row.find('th'):
                continue

            # Extract NOC code and title from card header link
            link = row.select_one('.cardsheader a, td a[href*="OccProfile"], td a[href*="code="]')
            if not link:
                continue

            href = link.get('href', '')
            text = link.get_text(strip=True)

            # Extract NOC code from text or URL
            code_match = self.NOC_CODE_PATTERN.search(text) or self.NOC_CODE_PATTERN.search(href)
            if not code_match:
                continue

            noc_code = code_match.group(0)
            # Title is text after code (format: "72600.01 - Air pilots")
            title = text.replace(noc_code, '').strip(' -–')

            # Extract lead statement (cell with fa-book icon)
            lead_statement = None
            book_cell = row.select_one('td:has(.fa-book) .OaSISCardTDTextStyle, td:has(.fa-book) p, td:has(.fa-book) div')
            if book_cell:
                lead_statement = book_cell.get_text(strip=True)
            else:
                # Fallback: try finding cell with "Lead" in class or text pattern
                for td in row.select('td'):
                    td_text = td.get_text(strip=True)
                    # Lead statements typically describe what the occupation does
                    if len(td_text) > 50 and not td_text.startswith('Matching'):
                        if td.select_one('.fa-book'):
                            lead_statement = td_text
                            break

            # Extract TEER description (cell with fa-bookmark icon)
            teer_description = None
            bookmark_cell = row.select_one('td:has(.fa-bookmark) .OaSISCardTDTextStyle, td:has(.fa-bookmark) span.noFontStyle')
            if bookmark_cell:
                teer_description = bookmark_cell.get_text(strip=True)

            # Extract broad category (cell with fa-truck, fa-pen-alt, fa-handshake icons)
            broad_category_name = None
            for icon_class in ['fa-truck', 'fa-pen-alt', 'fa-handshake', 'fa-laptop', 'fa-stethoscope']:
                boc_cell = row.select_one(f'td:has(.{icon_class}) .OaSISCardTDTextStyle')
                if boc_cell:
                    broad_category_name = boc_cell.get_text(strip=True)
                    break

            # Extract matching criteria (cell with fa-search icon)
            matching_criteria = None
            search_cell = row.select_one('td:has(.fa-search) .OaSISCardTDTextStyle, td.topBorder .OaSISCardTDTextStyle')
            if search_cell:
                # Get full text including child spans
                matching_text = search_cell.get_text(separator=' ', strip=True)
                # Clean up "Matching search criteria Label, Job titles" format
                matching_criteria = matching_text.replace('Matching search criteria', '').strip()

            # Derive minor group and broad category from NOC code
            base_code = noc_code.split('.')[0]
            broad_category = int(base_code[0]) if base_code else None
            minor_group = base_code[:3] if len(base_code) >= 3 else None

            results.append(EnrichedSearchResult(
                noc_code=noc_code,
                title=title,
                url=href,
                lead_statement=lead_statement,
                teer_description=teer_description,
                broad_category_name=broad_category_name,
                matching_criteria=matching_criteria,
                broad_category=broad_category,
                minor_group=minor_group,
                minor_group_name=None,  # Not available from search HTML
                # These require profile fetch - left as None
                example_titles=None,
                mobility_progression=None,
                source_table=None,
                publication_date=None,
                top_skills=None,
                top_abilities=None,
                top_knowledge=None
            ))

        return results

    def extract_noc_hierarchy(self, noc_code: str) -> NOCHierarchy:
        """Extract NOC hierarchy from 5 or 7-digit code.

        NOC code structure: 72600 or 72600.01
          - 7 = Broad occupational category (first digit)
          - 2 = TEER category (second digit)
          - 72 = Major group (first 2 digits)
          - 726 = Minor group (first 3 digits)
          - 7260 = Unit group (first 4 digits)
          - 72600 = Full 5-digit NOC (can have .XX suffix)

        Args:
            noc_code: NOC code string (e.g., "72600.01" or "21232")

        Returns:
            NOCHierarchy with all breakdown fields
        """
        # Remove decimal suffix for parsing
        base_code = noc_code.split('.')[0]

        # Pad to 5 digits if shorter
        base_code = base_code.zfill(5)

        broad = int(base_code[0])
        teer = int(base_code[1])

        return NOCHierarchy(
            noc_code=noc_code,
            broad_category=broad,
            broad_category_name=BROAD_CATEGORIES.get(broad, "Unknown category"),
            teer_category=teer,
            teer_description=TEER_CATEGORIES.get(teer, "Unknown TEER category"),
            major_group=base_code[:2],
            minor_group=base_code[:3],
            unit_group=base_code[:4]
        )

    def parse_profile(self, html: str, code: str) -> Dict[str, Any]:
        """Parse profile HTML into structured data dict.

        Args:
            html: Raw HTML from OASIS profile page
            code: NOC code for this profile

        Returns:
            Dict with:
            - noc_code: str
            - title: str
            - noc_hierarchy: NOCHierarchy
            - main_duties: List[str]
            - work_activities: List[dict] with {text, level, max}
            - skills: List[dict] with {text, level, max}
            - abilities: List[dict] with {text, level, max}
            - knowledge: List[dict] with {text, level, max}
            - work_context: List[dict] with {text, level, max, dimension_type}
            - employment_requirements: List[str]
            - reference_attributes: ReferenceAttributes
            - interests: List[str] (for Annex builder)
            - personal_attributes: List[str] (for Annex builder)
            - career_mobility: Dict with 'from' and 'to' lists (for Annex builder)
        """
        soup = BeautifulSoup(html, 'lxml')

        # Extract reference attributes (includes interests, career_mobility, personal_attributes)
        ref_attrs = self._extract_reference_attributes(soup)

        # Convert interests to List[str] for annex builder
        interests_list = [i.name for i in ref_attrs.interests] if ref_attrs.interests else []

        return {
            'noc_code': code,
            'title': self._extract_profile_title(soup),
            'noc_hierarchy': self.extract_noc_hierarchy(code),
            'main_duties': self._extract_section_list(soup, 'Main duties'),
            'work_activities': self._extract_rating_items_with_levels(soup, 'Work Activities'),
            'skills': self._extract_rating_items_with_levels(soup, 'Skills'),
            'abilities': self._extract_rating_items_with_levels(soup, 'Abilities'),
            'knowledge': self._extract_rating_items_with_levels(soup, 'Knowledge') or self._extract_rating_items_with_levels(soup, 'General Learning'),
            'work_context': self._extract_work_context(soup),
            'employment_requirements': self._extract_section_list(soup, 'Employment requirements'),
            'reference_attributes': ref_attrs,
            # Top-level fields for Annex builder
            'interests': interests_list,
            'personal_attributes': ref_attrs.personal_attributes or [],
            'career_mobility': self._extract_career_mobility_dict(soup),
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

        DEPRECATED: Use _extract_rating_items_with_levels for enhanced data.
        Kept for backward compatibility.

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

    def _extract_rating_items_with_levels(self, soup: BeautifulSoup, section_name: str) -> List[Dict[str, Any]]:
        """Extract items from a rating-based section with proficiency levels.

        Args:
            soup: BeautifulSoup instance
            section_name: Name of section header

        Returns:
            List of dicts with structure:
            {
                "text": "Critical thinking",
                "level": 4,
                "max": 5,
                "element_id": None
            }
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

        # Extract items with proficiency levels
        items = []
        rows = panel_body.select('.wb-eqht-grd')

        for row in rows:
            cells = row.select('.OasisdescriptorRatingCell')
            if not cells:
                continue

            first_cell = cells[0]

            # Skip if first cell itself is a rating cell
            if first_cell.find('span', class_='scale-option-circle'):
                continue

            # Extract text
            text = first_cell.get_text(strip=True)

            # Skip header cells
            if not text or 'Proficiency' in text or 'level' in text or 'Importance' in text:
                continue

            # Extract proficiency level from rating circles
            # Look for all circle elements in the entire row
            all_circles = row.select('.scale-option-circle')

            if not all_circles:
                # No rating circles found - include item but with None values
                items.append({
                    "text": text,
                    "level": None,
                    "max": None,
                    "element_id": None
                })
                continue

            # Count total circles to determine max scale
            max_level = len(all_circles)

            # Count filled circles to determine proficiency level
            # OASIS uses FontAwesome icons: 'fas' for filled, 'far' for empty
            filled_count = 0
            for circle in all_circles:
                classes = circle.get('class', [])
                # 'fas' = solid (filled), 'far' = regular (empty)
                if 'fas' in classes:
                    filled_count += 1
                # Fallback: check for 'filled', 'active', or similar class
                elif any('filled' in c.lower() or 'active' in c.lower() for c in classes):
                    filled_count += 1
                # Also check for inline style indicating filled state
                elif circle.get('style') and ('background' in circle.get('style', '').lower()):
                    filled_count += 1

            # Try to extract element_id from data attributes
            element_id = None
            # Look for data-element-id or similar attributes on row or cells
            for attr in ['data-element-id', 'data-id', 'id']:
                if row.get(attr):
                    element_id = row.get(attr)
                    break
                if first_cell.get(attr):
                    element_id = first_cell.get(attr)
                    break

            items.append({
                "text": text,
                "level": filled_count,
                "max": max_level,
                "element_id": element_id
            })

        return items

    def _extract_work_context(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract work context items with dimension types and proficiency levels.

        Args:
            soup: BeautifulSoup instance

        Returns:
            List of dicts with structure:
            {
                "text": "Degree of responsibility for work outcomes",
                "dimension_type": "Degree of responsibility",
                "level": 4,
                "max": 5
            }
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

        # PRIMARY: Try standard structure with Descriptors-Rating-By-MeasuredDimension-Div
        dimension_divs = panel_body.select('.Descriptors-Rating-By-MeasuredDimension-Div')

        if dimension_divs:
            logger.info("Work Context extraction using primary selector (.Descriptors-Rating-By-MeasuredDimension-Div)")

            for div in dimension_divs:
                # Work Context structure:
                # - First col-xs-6 cell: dimension type (e.g., "Structured versus Unstructured Work")
                # - Second col-xs-6 cell: item description (e.g., "Degree of freedom...")
                # - Fourth col-xs-6 cell: rating with circles

                all_cells = div.select('.col-xs-6')

                if len(all_cells) >= 2:
                    # First cell is dimension type
                    dimension_type = all_cells[0].get_text(strip=True)

                    # Second cell is item description
                    item_text = all_cells[1].get_text(strip=True)

                    # Find rating cell (contains circles)
                    level = None
                    max_level = None
                    for cell in all_cells:
                        circles = cell.select('.scale-option-circle')
                        if circles:
                            # Count filled circles (fas = solid, far = empty)
                            level = sum(1 for c in circles if 'fas' in c.get('class', []))
                            max_level = len(circles)
                            break

                    # Only add if we have actual item text (not just dimension type)
                    if item_text and item_text != dimension_type and 'Proficiency' not in item_text and 'level' not in item_text:
                        items.append({
                            "text": item_text,
                            "dimension_type": dimension_type,
                            "level": level,
                            "max": max_level
                        })

        else:
            # FALLBACK 1: Try alternative class names
            logger.info("Work Context primary selector failed, trying fallback 1 (alternative class names)")
            alt_divs = panel_body.select('.MeasuredDimension-Div, .work-context-dimension, .dimension-section')

            if alt_divs:
                # Same logic as primary
                for div in alt_divs:
                    dimension_type = "Unknown"
                    dimension_header = div.find(['strong', 'b', 'h4', 'h5'])
                    if dimension_header:
                        dimension_type = dimension_header.get_text(strip=True)

                    rows = div.select('.wb-eqht-grd')
                    for row in rows:
                        cells = row.select('.col-xs-6.pad10, .OasisdescriptorRatingCell')
                        if cells:
                            first_cell = cells[0]
                            if first_cell.find('span', class_='scale-option-circle'):
                                continue

                            text = first_cell.get_text(strip=True)
                            if text and text != dimension_type:
                                circles = row.select('.scale-option-circle')
                                level = sum(1 for c in circles if 'fas' in c.get('class', []) or any('filled' in cls.lower() or 'active' in cls.lower() for cls in c.get('class', [])))
                                max_level = len(circles) if circles else 5

                                items.append({
                                    "text": text,
                                    "dimension_type": dimension_type,
                                    "level": level,
                                    "max": max_level
                                })

            else:
                # FALLBACK 2: Structural fallback - find headers and items
                logger.info("Work Context fallback 1 failed, trying fallback 2 (structural parsing)")
                headers = panel_body.find_all(['h4', 'h5', 'strong'])

                if headers:
                    for header in headers:
                        dimension_type = header.get_text(strip=True)

                        # Find all items after this header until next header
                        sibling = header.find_next_sibling()
                        while sibling and sibling.name not in ['h4', 'h5', 'strong']:
                            # Look for rating rows
                            if sibling.name == 'div':
                                rows = sibling.select('.wb-eqht-grd')
                                for row in rows:
                                    cells = row.select('.col-xs-6.pad10, .OasisdescriptorRatingCell')
                                    if cells:
                                        first_cell = cells[0]
                                        if first_cell.find('span', class_='scale-option-circle'):
                                            continue

                                        text = first_cell.get_text(strip=True)
                                        if text:
                                            circles = row.select('.scale-option-circle')
                                            level = sum(1 for c in circles if 'fas' in c.get('class', []) or any('filled' in cls.lower() or 'active' in cls.lower() for cls in c.get('class', [])))
                                            max_level = len(circles) if circles else 5

                                            items.append({
                                                "text": text,
                                                "dimension_type": dimension_type,
                                                "level": level,
                                                "max": max_level
                                            })

                            sibling = sibling.find_next_sibling()

                else:
                    # FALLBACK 3: No dimension structure detected
                    logger.warning("Work Context dimension extraction failed, using fallback 3 (dimension_type='Unknown')")

                    # Extract all items without dimension classification
                    rows = panel_body.select('.wb-eqht-grd')
                    for row in rows:
                        cells = row.select('.col-xs-6.pad10, .OasisdescriptorRatingCell')
                        if cells:
                            first_cell = cells[0]
                            if first_cell.find('span', class_='scale-option-circle'):
                                continue

                            text = first_cell.get_text(strip=True)
                            if text:
                                circles = row.select('.scale-option-circle')
                                level = sum(1 for c in circles if 'fas' in c.get('class', []) or any('filled' in cls.lower() or 'active' in cls.lower() for cls in c.get('class', [])))
                                max_level = len(circles) if circles else 5

                                items.append({
                                    "text": text,
                                    "dimension_type": "Unknown",
                                    "level": level,
                                    "max": max_level
                                })

        return items

    def _extract_also_known_as(self, soup: BeautifulSoup) -> List[str]:
        """Extract 'Also known as' titles from Overview."""
        # Look for text containing "Also known as" followed by a list
        also_known = []

        # Try to find in profile summary or first panel
        for div in soup.select('.panel-body'):
            text = div.get_text()
            if 'Also known as' in text or 'also known as' in text:
                # Find the ul/li items after
                ul = div.find('ul')
                if ul:
                    also_known = [li.get_text(strip=True) for li in ul.find_all('li')]
                    break

        return also_known

    def _extract_interests(self, soup: BeautifulSoup) -> List[Interest]:
        """Extract interests from Interests section."""
        interests = []

        h3 = soup.find('h3', string='Interests')
        if not h3:
            h3 = soup.find('h3', string=lambda x: x and 'Interest' in x)

        if h3:
            panel = h3.find_parent('div', class_='panel')
            if panel:
                panel_body = panel.find('div', class_='panel-body')
                if panel_body:
                    # Interests may have name + description pairs
                    for item in panel_body.select('.wb-eqht-grd, li'):
                        text = item.get_text(strip=True)
                        if text:
                            # Try to split name: description
                            if ':' in text:
                                parts = text.split(':', 1)
                                interests.append(Interest(
                                    name=parts[0].strip(),
                                    description=parts[1].strip() if len(parts) > 1 else None
                                ))
                            else:
                                interests.append(Interest(name=text))

        return interests

    def _extract_career_mobility(self, soup: BeautifulSoup) -> List[CareerMobilityPath]:
        """Extract career mobility paths from Overview."""
        paths = []

        # Look for career mobility section
        h3 = soup.find('h3', string=lambda x: x and 'mobility' in x.lower() if x else False)
        if not h3:
            return paths

        panel = h3.find_parent('div', class_='panel')
        if panel:
            panel_body = panel.find('div', class_='panel-body')
            if panel_body:
                for link in panel_body.find_all('a'):
                    href = link.get('href', '')
                    title = link.get_text(strip=True)

                    # Extract NOC code from href if present
                    code_match = self.NOC_CODE_PATTERN.search(href)
                    noc_code = code_match.group(0) if code_match else None

                    if title:
                        paths.append(CareerMobilityPath(
                            title=title,
                            noc_code=noc_code
                        ))

        return paths

    def _extract_career_mobility_dict(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract career mobility paths as dict with 'from' and 'to' keys.

        Looks for entry paths (where workers come from) and advancement paths
        (where workers can go to).

        Returns:
            Dict with 'from' (entry paths) and 'to' (advancement paths)
        """
        result = {'from': [], 'to': []}

        # Look for career mobility section
        h3 = soup.find('h3', string=lambda x: x and 'mobility' in x.lower() if x else False)
        if not h3:
            return result

        panel = h3.find_parent('div', class_='panel')
        if not panel:
            return result

        panel_body = panel.find('div', class_='panel-body')
        if not panel_body:
            return result

        # Try to find entry/advancement sub-sections
        current_section = None

        for elem in panel_body.children:
            if not hasattr(elem, 'name'):
                continue

            # Check for section headers
            if elem.name in ['h4', 'h5', 'strong', 'b', 'p']:
                text = elem.get_text(strip=True).lower()
                if 'entry' in text or 'from' in text or 'come from' in text:
                    current_section = 'from'
                elif 'advancement' in text or 'progress' in text or 'move to' in text or 'to' in text:
                    current_section = 'to'

            # Extract links from lists or divs
            if elem.name in ['ul', 'div']:
                links = elem.find_all('a')
                for link in links:
                    title = link.get_text(strip=True)
                    if title:
                        if current_section:
                            result[current_section].append(title)
                        else:
                            # Default to 'from' if no section identified
                            result['from'].append(title)

        # Fallback: if no structure found, get all links
        if not result['from'] and not result['to']:
            for link in panel_body.find_all('a'):
                title = link.get_text(strip=True)
                if title:
                    result['from'].append(title)

        return result

    def _extract_personal_attributes(self, soup: BeautifulSoup) -> List[str]:
        """Extract personal attributes from profile."""
        # Try multiple section names
        for section_name in ['Personal attributes', 'Personal qualities', 'Key attributes']:
            items = self._extract_section_list(soup, section_name)
            if items:
                return items

        # Also check rating-based personal attributes
        items = self._extract_rating_items(soup, 'Personal Attributes')
        if items:
            # Convert from dict format if needed
            if items and isinstance(items[0], dict):
                return [item.get('text', str(item)) for item in items]
            return items

        return []

    def _extract_reference_attributes(self, soup: BeautifulSoup) -> ReferenceAttributes:
        """Extract reference attributes from Overview tab.

        Looks for:
        - "Also known as" section -> example_titles
        - "Interests" section -> interests with descriptions
        - "Career mobility" section -> career paths with NOC codes
        - Employment requirements (already extracted) -> job_requirements
        - "Personal attributes" or "Core competencies" sections

        Args:
            soup: BeautifulSoup instance

        Returns:
            ReferenceAttributes with all available data
        """
        # Example titles from "Also known as"
        example_titles = self._extract_also_known_as(soup)

        # Interests with descriptions
        interests = self._extract_interests(soup)

        # Career mobility paths
        career_mobility = self._extract_career_mobility(soup)

        # Personal attributes
        personal_attributes = self._extract_personal_attributes(soup)

        # Core competencies (if present)
        core_competencies = self._extract_section_list(soup, 'Core competencies')

        return ReferenceAttributes(
            example_titles=example_titles,
            interests=interests,
            career_mobility=career_mobility,
            personal_attributes=personal_attributes,
            core_competencies=core_competencies
        )


# Module-level singleton for easy import
parser = OASISParser()
