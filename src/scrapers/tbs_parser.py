"""BeautifulSoup parsers for TBS occupational group pages.

Extracts structured data from TBS HTML pages with graceful
error handling for parse failures.
"""

import logging
import re
from typing import Dict, List, Any, Optional

from bs4 import BeautifulSoup, Tag


logger = logging.getLogger(__name__)


def parse_occupational_groups_table(html: bytes) -> List[Dict[str, Any]]:
    """Parse the TBS occupational groups concordance table.

    Extracts group information from the main table at:
    https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html

    Args:
        html: Raw HTML bytes

    Returns:
        List of dicts with keys:
            - group_code: Abbreviation (e.g., "AI", "CP")
            - code: Numeric code (e.g., "402")
            - group_name: Full group name
            - subgroup: Subgroup name or None
            - definition_url: URL to definition page (or None)
            - job_evaluation_standard_url: URL to job eval standard (or None)
            - qualification_standard_url: URL to qualification standard (or None)
            - rates_of_pay_represented_url: URL for represented employees (or None)
            - rates_of_pay_unrepresented_url: URL for unrepresented employees (or None)
    """
    soup = BeautifulSoup(html, "lxml")
    groups = []

    try:
        table = soup.find("table")
        if not table:
            logger.error("No table found in occupational groups page")
            return groups

        rows = table.find_all("tr")
        if len(rows) < 2:
            logger.error("Table has no data rows")
            return groups

        # Skip header row
        for row_idx, row in enumerate(rows[1:], start=1):
            try:
                cells = row.find_all("td")
                if len(cells) < 12:
                    logger.warning(
                        f"Row {row_idx} has {len(cells)} cells, expected 12, skipping"
                    )
                    continue

                # Extract cell values
                # Columns: 0=Group abbreviation, 1=Code, 2=Occupational Group (post 1999),
                # 3=Group, 4=Subgroup, 5=Definition, 6=Job eval standard,
                # 7=Qualification standard, 8=Bargaining update, 9=Collective agreement,
                # 10=Rates of pay represented, 11=Rates of pay unrepresented
                group_code = cells[0].get_text(strip=True)
                code = cells[1].get_text(strip=True)
                group_name = cells[3].get_text(strip=True)
                subgroup_text = cells[4].get_text(strip=True)
                subgroup = subgroup_text if subgroup_text and subgroup_text != "N/A" else None

                # Extract URLs from link cells
                definition_url = _extract_link(cells[5])
                job_eval_url = _extract_link(cells[6])
                qualification_url = _extract_link(cells[7])
                rates_represented_url = _extract_link(cells[10])
                rates_unrepresented_url = _extract_link(cells[11])

                groups.append({
                    "group_code": group_code,
                    "code": code,
                    "group_name": group_name,
                    "subgroup": subgroup,
                    "definition_url": definition_url,
                    "job_evaluation_standard_url": job_eval_url,
                    "qualification_standard_url": qualification_url,
                    "rates_of_pay_represented_url": rates_represented_url,
                    "rates_of_pay_unrepresented_url": rates_unrepresented_url,
                })

            except Exception as e:
                logger.warning(f"Error parsing row {row_idx}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error parsing occupational groups table: {e}")

    return groups


def _extract_link(cell: Tag) -> Optional[str]:
    """Extract href from first link in cell, or None if no link."""
    link = cell.find("a")
    if link and link.get("href"):
        href = link["href"]
        # Convert relative URLs to absolute
        if href.startswith("/"):
            return f"https://www.canada.ca{href}"
        return href
    return None


def parse_definition_page(
    html: bytes, group_code: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Parse the TBS occupational group definitions page.

    Extracts definitions, inclusions, and exclusions from:
    https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups/definitions.html

    Args:
        html: Raw HTML bytes
        group_code: If provided, return only that group's data.
            If None, return all groups found.

    Returns:
        List of dicts with keys:
            - group_code: Group code from anchor (e.g., "AI")
            - subgroup: Subgroup code or None (e.g., "NOP" for AI-NOP)
            - heading_text: Full heading text
            - definition: Definition text
            - inclusions: List of {statement, order} dicts
            - exclusions: List of {statement, order} dicts
    """
    soup = BeautifulSoup(html, "lxml")
    definitions = []

    try:
        # Find all definition headings (h3 or h4 with id starting with "def-")
        headings = soup.find_all(["h3", "h4"], id=lambda x: x and x.startswith("def-"))

        for heading in headings:
            try:
                # Extract group code from id
                heading_id = heading.get("id", "")
                # id format: "def-ai" or "def-ai-nop"
                parts = heading_id.replace("def-", "").upper().split("-")
                extracted_code = parts[0] if parts else None
                subgroup = "-".join(parts[1:]) if len(parts) > 1 else None

                # Filter by group_code if specified
                if group_code and extracted_code != group_code.upper():
                    continue

                heading_text = heading.get_text(strip=True)

                # Extract definition text (first p after heading that isn't a section)
                definition = _extract_definition_text(heading)

                # Extract inclusions
                inclusions = _extract_list_items(heading, "inclusions")

                # Extract exclusions
                exclusions = _extract_list_items(heading, "exclusions")

                definitions.append({
                    "group_code": extracted_code,
                    "subgroup": subgroup if subgroup else None,
                    "heading_text": heading_text,
                    "definition": definition,
                    "inclusions": inclusions,
                    "exclusions": exclusions,
                })

            except Exception as e:
                logger.warning(f"Error parsing heading {heading.get('id')}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error parsing definition page: {e}")

    return definitions


def _extract_definition_text(heading: Tag) -> str:
    """Extract definition text from the section after a heading.

    The definition is typically the first <p> tag(s) after the heading,
    before any Inclusions/Exclusions sections.
    """
    definition_parts = []

    # Walk siblings until we hit Inclusions/Exclusions section or next def heading
    for sibling in heading.find_next_siblings():
        if sibling.name in ["h3", "h4", "h5"]:
            text = sibling.get_text(strip=True).lower()
            # Stop at Inclusions/Exclusions or next definition
            if "inclusion" in text or "exclusion" in text or sibling.get("id", "").startswith("def-"):
                break
        elif sibling.name == "section":
            # Check if section contains Inclusions/Exclusions heading
            section_h4 = sibling.find(["h4", "h5"])
            if section_h4:
                text = section_h4.get_text(strip=True).lower()
                if "inclusion" in text or "exclusion" in text or section_h4.get("id", "").startswith("def-"):
                    break
        elif sibling.name == "p":
            text = sibling.get_text(strip=True)
            if text:
                definition_parts.append(text)
        elif sibling.name in ["ol", "ul"]:
            # Stop if we hit a list (likely Inclusions without heading)
            break

    return " ".join(definition_parts)


def _extract_list_items(heading: Tag, section_type: str) -> List[Dict[str, Any]]:
    """Extract ordered list items from an Inclusions or Exclusions section.

    Args:
        heading: The group definition heading to search from
        section_type: Either "inclusions" or "exclusions"

    Returns:
        List of {statement, order} dicts
    """
    items = []

    # Search through siblings for sections or direct headings
    for sibling in heading.find_next_siblings():
        # Stop at next group definition
        if sibling.name in ["h3", "h4"] and sibling.get("id", "").startswith("def-"):
            break

        # Handle <section> elements containing the heading and list
        if sibling.name == "section":
            section_h4 = sibling.find(["h4", "h5"])
            if section_h4:
                text = section_h4.get_text(strip=True).lower()
                if section_type.lower() in text:
                    # Found the section, extract list items
                    ol = sibling.find("ol")
                    if ol:
                        for order, li in enumerate(ol.find_all("li", recursive=False), 1):
                            statement = li.get_text(strip=True)
                            if statement:
                                items.append({"statement": statement, "order": order})
                    return items
                # Check if this section is a subgroup definition (stop searching)
                elif section_h4.get("id", "").startswith("def-"):
                    break

        # Handle direct h4/h5 headings (without section wrapper)
        if sibling.name in ["h4", "h5"]:
            text = sibling.get_text(strip=True).lower()
            if section_type.lower() in text:
                # Found the section heading, now find the list
                ol = sibling.find_next_sibling("ol")
                if ol:
                    for order, li in enumerate(ol.find_all("li", recursive=False), 1):
                        statement = li.get_text(strip=True)
                        if statement:
                            items.append({"statement": statement, "order": order})
                return items

    return items


def parse_allocation_guide(html: bytes) -> List[Dict[str, Any]]:
    """Parse the TBS allocation guide and label paragraphs.

    Extracts paragraphs from the allocation guide at:
    https://www.canada.ca/en/treasury-board-secretariat/services/classification/job-evaluation/guide-allocating-positions-using-occupational-group-definitions.html

    Labels paragraphs as P1, P2, P3... for provenance mapping.

    Args:
        html: Raw HTML bytes

    Returns:
        List of dicts with keys:
            - paragraph_label: Sequential label (P1, P2, P3...)
            - content: Paragraph text
            - section: Parent heading text
    """
    soup = BeautifulSoup(html, "lxml")
    paragraphs = []
    counter = 1

    try:
        # Find main content area
        main_content = soup.find("main") or soup.find("article") or soup.body

        if not main_content:
            logger.error("No main content found in allocation guide")
            return paragraphs

        current_section = "Introduction"

        # Walk through content
        for element in main_content.find_all(["h2", "h3", "h4", "p", "li"]):
            try:
                if element.name in ["h2", "h3", "h4"]:
                    section_text = element.get_text(strip=True)
                    if section_text:
                        current_section = section_text
                elif element.name in ["p", "li"]:
                    text = element.get_text(strip=True)
                    # Filter out empty or very short content
                    if text and len(text) > 20:
                        paragraphs.append({
                            "paragraph_label": f"P{counter}",
                            "content": text,
                            "section": current_section,
                        })
                        counter += 1
            except Exception as e:
                logger.warning(f"Error processing element: {e}")
                continue

    except Exception as e:
        logger.error(f"Error parsing allocation guide: {e}")

    return paragraphs


def validate_parsed_group(group: Dict[str, Any]) -> List[str]:
    """Validate a parsed group definition.

    Checks for required fields and returns list of validation errors.

    Args:
        group: Parsed group dict from parse_definition_page

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check group_code
    if not group.get("group_code"):
        errors.append("Missing group_code")
    elif not re.match(r"^[A-Z]{2,4}$", group["group_code"]):
        errors.append(f"Invalid group_code format: {group['group_code']}")

    # Check definition
    if not group.get("definition"):
        errors.append("Missing definition")
    elif len(group["definition"]) < 20:
        errors.append(f"Definition too short ({len(group['definition'])} chars)")

    # Check inclusions structure
    inclusions = group.get("inclusions", [])
    if not isinstance(inclusions, list):
        errors.append("Inclusions is not a list")
    else:
        for i, inc in enumerate(inclusions):
            if not isinstance(inc, dict):
                errors.append(f"Inclusion {i} is not a dict")
            elif not inc.get("statement"):
                errors.append(f"Inclusion {i} missing statement")
            elif not inc.get("order"):
                errors.append(f"Inclusion {i} missing order")

    # Check exclusions structure
    exclusions = group.get("exclusions", [])
    if not isinstance(exclusions, list):
        errors.append("Exclusions is not a list")
    else:
        for i, exc in enumerate(exclusions):
            if not isinstance(exc, dict):
                errors.append(f"Exclusion {i} is not a dict")
            elif not exc.get("statement"):
                errors.append(f"Exclusion {i} missing statement")
            elif not exc.get("order"):
                errors.append(f"Exclusion {i} missing order")

    return errors
