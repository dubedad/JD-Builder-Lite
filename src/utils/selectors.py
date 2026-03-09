"""CSS selector abstraction for OASIS HTML parsing."""

from typing import List

# Selector definitions with primary and fallback options
# Note: These are educated guesses based on common patterns.
# They will be refined during live testing in Plan 03.
SELECTORS = {
    "search_results": {
        "primary": "#OaSISSearchResultsTable tbody tr",
        "fallback": "table[aria-label*='Search results'] tbody tr",
    },
    "result_link": {
        "primary": "a[href*='OASISOccProfile']",
        "fallback": "a[href*='OccProfile']",
    },
    "profile_title": {
        "primary": "h1",
        "fallback": "div.profile-header h1",
    },
    "main_duties": {
        "primary": "#main-duties li, #MainDuties li, .main-duties li",
        "fallback": "section:has(h2:contains('Duties')) li",
    },
    "work_activities": {
        "primary": "#work-activities li, .work-activities li",
        "fallback": "section:has(h2:contains('Activities')) li",
    },
    "skills": {
        "primary": "#skills li, .skills-list li",
        "fallback": "section:has(h2:contains('Skills')) li",
    },
    "abilities": {
        "primary": "#abilities li, .abilities-list li",
        "fallback": "section:has(h2:contains('Abilities')) li",
    },
    "knowledge": {
        "primary": "#knowledge li, .knowledge-list li",
        "fallback": "section:has(h2:contains('Knowledge')) li",
    },
    "work_context": {
        "primary": "#work-context li, .work-context li, table.work-context tr",
        "fallback": "section:has(h2:contains('Context')) li",
    },
    "employment_requirements": {
        "primary": "#employment-requirements li, .requirements li",
        "fallback": "section:has(h2:contains('Requirements')) li",
    },
}


def get_selector(element: str) -> str:
    """Get primary CSS selector for element.

    Args:
        element: Element name from SELECTORS dict

    Returns:
        Primary CSS selector string

    Raises:
        KeyError: If element not found in SELECTORS
    """
    return SELECTORS[element]["primary"]


def get_fallback(element: str) -> str:
    """Get fallback CSS selector for element.

    Args:
        element: Element name from SELECTORS dict

    Returns:
        Fallback CSS selector string

    Raises:
        KeyError: If element not found in SELECTORS
    """
    return SELECTORS[element]["fallback"]


def get_all_selectors(element: str) -> List[str]:
    """Get all selectors for element (primary and fallback).

    Args:
        element: Element name from SELECTORS dict

    Returns:
        List containing [primary, fallback] selectors

    Raises:
        KeyError: If element not found in SELECTORS
    """
    return [
        SELECTORS[element]["primary"],
        SELECTORS[element]["fallback"]
    ]
