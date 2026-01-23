"""Build Annex data structure from NOC profile and manager selections.

The Annex section contains unused NOC reference attributes that weren't
selected for the main JD body but may be useful for recruitment, career
development, and job analysis.
"""

from typing import List, Dict, Any, Set
from datetime import datetime
from src.models.export_models import AnnexSection, AnnexData, SelectionMetadata


def build_annex_data(
    raw_noc_data: Dict[str, Any],
    manager_selections: List[SelectionMetadata],
    noc_code: str,
    scraped_at: datetime
) -> AnnexData:
    """
    Build Annex section data from NOC profile.

    Identifies unused NOC attributes by comparing raw data against
    manager selections. Fixed category order per CONTEXT.md:
    1. Job Requirements
    2. Career Mobility
    3. Interests (Holland Codes)
    4. Personal Suitability (Placement Criteria)

    Always returns AnnexData with all 4 sections (empty state handled).

    Args:
        raw_noc_data: Dict from parser.parse_profile() with interests,
                      personal_attributes, career_mobility, employment_requirements
        manager_selections: List of SelectionMetadata from export request
        noc_code: NOC code for source attribution
        scraped_at: When the NOC data was retrieved

    Returns:
        AnnexData with all 4 sections in fixed order
    """
    # Extract texts already used in JD selections
    used_texts = {sel.text for sel in manager_selections}

    # Build sections in fixed order
    sections = [
        _build_job_requirements(raw_noc_data.get('employment_requirements', []), used_texts),
        _build_career_mobility(raw_noc_data.get('career_mobility', {}), used_texts),
        _build_interests(raw_noc_data.get('interests', []), used_texts),
        _build_personal_suitability(raw_noc_data.get('personal_attributes', []), used_texts)
    ]

    return AnnexData(
        sections=sections,
        source_noc_code=noc_code,
        retrieved_at=scraped_at
    )


def _build_job_requirements(items: List[str], used: Set[str]) -> AnnexSection:
    """Build Job Requirements section from employment_requirements.

    Args:
        items: Employment requirements from NOC profile
        used: Set of texts already selected by manager

    Returns:
        AnnexSection with unused requirements as paragraphs
    """
    unused = [item for item in items if item not in used]
    return AnnexSection(
        title='Job Requirements',
        category='job_requirements',
        items=unused,
        format_type='paragraph'
    )


def _build_career_mobility(mobility_data: Dict[str, Any], used: Set[str]) -> AnnexSection:
    """Build Career Mobility section with Entry/Advancement grouping.

    Args:
        mobility_data: Dict with 'from' (entry paths) and 'to' (advancement paths)
        used: Set of texts already selected by manager

    Returns:
        AnnexSection with grouped list format
    """
    from_paths = mobility_data.get('from', [])
    to_paths = mobility_data.get('to', [])

    from_unused = [p for p in from_paths if p not in used]
    to_unused = [p for p in to_paths if p not in used]

    items = []
    if from_unused:
        items.append('Entry Paths:')
        items.extend([f'  - {p}' for p in from_unused])
    if to_unused:
        items.append('Advancement Paths:')
        items.extend([f'  - {p}' for p in to_unused])

    return AnnexSection(
        title='Career Mobility',
        category='career_mobility',
        items=items,
        format_type='grouped_list'
    )


def _build_interests(items: List[str], used: Set[str]) -> AnnexSection:
    """Build Interests (Holland Codes) section.

    Args:
        items: Interest names from NOC profile
        used: Set of texts already selected by manager

    Returns:
        AnnexSection with bullet list format
    """
    unused = [item for item in items if item not in used]
    return AnnexSection(
        title='Interests (Holland Codes)',
        category='interests',
        items=unused,
        format_type='list'
    )


def _build_personal_suitability(items: List[str], used: Set[str]) -> AnnexSection:
    """Build Personal Suitability (Placement Criteria) section.

    Args:
        items: Personal attributes from NOC profile
        used: Set of texts already selected by manager

    Returns:
        AnnexSection with bullet list format
    """
    unused = [item for item in items if item not in used]
    return AnnexSection(
        title='Personal Suitability (Placement Criteria)',
        category='personal_suitability',
        items=unused,
        format_type='list'
    )
