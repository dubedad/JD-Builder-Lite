"""Build provenance maps from allocation results for API responses.

Extracts TBS source metadata and paragraph references for audit trail.
"""

import re
from typing import Dict, List
from src.matching.models import AllocationResult, GroupRecommendation
from src.models.allocation import ProvenanceDetail
from src.storage.repository import OccupationalGroupRepository
from src.storage.db_manager import get_db


def extract_paragraph_labels(check_text: str) -> List[str]:
    """Extract paragraph labels (I1, I2, E1, etc.) from reasoning text.

    Per RESEARCH.md: Labels follow pattern like "I1", "I3", "E2".

    Args:
        check_text: Inclusion or exclusion check text from LLM reasoning

    Returns:
        List of paragraph labels found (e.g., ["I1", "I3"])
    """
    if not check_text:
        return []
    # Match patterns like "I1", "I3", "E2" in reasoning text
    return re.findall(r'\b([IE]\d+)\b', check_text)


def build_provenance_map(result: AllocationResult) -> Dict[str, ProvenanceDetail]:
    """Build provenance map from AllocationResult.

    Per CONTEXT.md: Provenance links embedded in each recommendation.
    Per RESEARCH.md Pattern 3: Structure as flat dict with group_code keys.

    Structure (2 levels deep):
    {
        "CS": ProvenanceDetail(...),
        "AI": ProvenanceDetail(...),
    }

    Args:
        result: Complete allocation result from matching engine

    Returns:
        Dict mapping group_code to ProvenanceDetail
    """
    provenance_map = {}

    for rec in result.top_recommendations:
        with get_db() as conn:
            repo = OccupationalGroupRepository(conn)
            scrape_info = repo.get_group_provenance(rec.group_id)

        # Extract inclusion/exclusion paragraph labels from reasoning
        inclusions_used = extract_paragraph_labels(rec.inclusion_check)
        exclusions_checked = extract_paragraph_labels(rec.exclusion_check)

        # Handle case where scrape_info might not have all fields
        scraped_at = scrape_info.get('scraped_at', '') if scrape_info else ''
        archive_path = scrape_info.get('archive_path') if scrape_info else None
        data_source_id = scrape_info.get('source_provenance_id', 0) if scrape_info else 0

        provenance_map[rec.group_code] = ProvenanceDetail(
            source_type="TBS Occupational Group Definition",
            url=rec.provenance_url,
            definition_paragraph=rec.provenance_paragraph or "Definition",
            inclusions_referenced=inclusions_used,
            exclusions_checked=exclusions_checked,
            scraped_at=scraped_at,
            archive_path=archive_path,
            data_source_id=data_source_id
        )

    return provenance_map


def build_confidence_summary(result: AllocationResult) -> Dict[str, float]:
    """Build quick lookup dict of confidence scores.

    Per CONTEXT.md: confidence_summary = {group_code: confidence}

    Args:
        result: Complete allocation result

    Returns:
        Dict mapping group_code to confidence score
    """
    return {
        rec.group_code: rec.confidence
        for rec in result.top_recommendations
    }


__all__ = ['build_provenance_map', 'extract_paragraph_labels', 'build_confidence_summary']
