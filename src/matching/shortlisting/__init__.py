"""Shortlisting module for pre-filtering candidate occupational groups.

This module provides semantic similarity matching and labels-based confidence boost
to reduce token costs and improve LLM focus by identifying viable candidates before
expensive LLM classification.

Per CONTEXT.md: "Hybrid approach - match all groups but boost confidence if labels.csv
supports the match"
"""

from typing import List, Dict
import re

# Lazy imports to avoid loading heavy models unless needed
_semantic_matcher = None
_labels_booster = None

# Keyword-based group code matching for obvious job titles
# This helps when semantic matching fails due to definition preamble
# Format: { 'group_code': ['keyword1', 'keyword2', ...] }
TITLE_KEYWORD_GROUPS = {
    'AS': ['administrative', 'admin assistant', 'administrative assistant', 'executive assistant', 'clerical'],
    'IT': ['software', 'developer', 'programmer', 'information technology', 'it specialist', 'systems analyst', 'computer'],
    'PR': ['printer', 'printing', 'press operator', 'print technician'],
    'EC': ['economist', 'policy analyst', 'socio-economic', 'statistician'],
    'CR': ['clerk', 'data entry', 'records', 'registry'],
    'ST': ['secretary', 'stenographer', 'typist'],
    'PM': ['program manager', 'project manager', 'program officer'],
    'PE': ['human resources', 'hr specialist', 'staffing', 'personnel'],
    'FI': ['accountant', 'financial', 'finance officer', 'comptroller'],
    'EN': ['engineer', 'engineering'],
    'NU': ['nurse', 'nursing', 'registered nurse', 'rn'],
    'LS': ['librarian', 'library', 'archivist'],
    'TR': ['translator', 'translation', 'interpreter'],
}


def _get_keyword_boost(group_code: str, jd_text: str) -> float:
    """
    Return a boost (0.0-0.15) if JD text contains keywords associated with group.

    This helps with obvious matches where semantic similarity fails due to
    bureaucratic definition text.

    Args:
        group_code: TBS group code
        jd_text: Job description text (title + activities)

    Returns:
        Boost value: 0.15 for strong match, 0.0 for no match
    """
    keywords = TITLE_KEYWORD_GROUPS.get(group_code, [])
    if not keywords:
        return 0.0

    jd_lower = jd_text.lower()
    for keyword in keywords:
        if keyword in jd_lower:
            return 0.15  # Significant boost for keyword match

    return 0.0


def _get_semantic_matcher():
    """Get or create the semantic matcher singleton."""
    global _semantic_matcher
    if _semantic_matcher is None:
        from .semantic_matcher import SemanticMatcher
        _semantic_matcher = SemanticMatcher()
    return _semantic_matcher


def _get_labels_booster():
    """Get or create the labels booster singleton."""
    global _labels_booster
    if _labels_booster is None:
        from .labels_matcher import LabelsBooster
        _labels_booster = LabelsBooster()
    return _labels_booster


def shortlist_with_all_signals(
    jd_text: str,
    groups: List[Dict],
    min_similarity: float = 0.3,
    max_candidates: int = 10
) -> List[Dict]:
    """
    Shortlist candidates using all available signals.

    Per CONTEXT.md decision: "Inclusion statements: Use for shortlisting candidates only,
    not for scoring or evidence"

    Signal usage:
    1. Semantic similarity to DEFINITION - primary signal for LLM
    2. Semantic similarity to INCLUSIONS - used for RANKING when inclusions match better
       than definitions (e.g., IT group has legal preamble in definition but clear inclusions)
    3. Labels.csv boost - additive boost for ordering

    Args:
        jd_text: Combined Client-Service Results + Key Activities
        groups: List of group dicts from repository (with inclusions)
        min_similarity: Threshold (default 0.3 per CONTEXT.md)
        max_candidates: Max candidates to return (default 10)

    Returns:
        List of dicts sorted by combined_score desc:
        {
            'group': original group dict,
            'semantic_similarity': float,  # similarity to definition (for LLM)
            'inclusion_match': bool,       # True if inclusions helped shortlist
            'best_inclusion_sim': float,   # best inclusion similarity (for ranking)
            'labels_boost': float,
            'combined_score': float        # max(definition, inclusion) + labels_boost
        }
    """
    matcher = _get_semantic_matcher()
    booster = _get_labels_booster()

    candidates = []

    for group in groups:
        # Calculate semantic similarity to definition
        definition = group.get('definition', '')
        if not definition:
            continue

        semantic_similarity = matcher.compute_similarity(jd_text, definition)

        # Calculate best inclusion similarity for ranking
        # This helps groups like IT where definition has legal preamble
        # but inclusions clearly describe the work (e.g., "developing software")
        inclusion_match = False
        best_inclusion_sim = 0.0
        inclusions = group.get('inclusions', [])
        if inclusions and isinstance(inclusions, list):
            for inclusion in inclusions:
                if isinstance(inclusion, str):
                    inclusion_sim = matcher.compute_similarity(jd_text, inclusion)
                    if inclusion_sim > best_inclusion_sim:
                        best_inclusion_sim = inclusion_sim
                    # Flag inclusion_match if any inclusion matches well (>= 0.4)
                    if inclusion_sim >= 0.4:
                        inclusion_match = True

        # Get labels boost (0.0-0.1 range)
        group_code = group.get('group_code', '')
        labels_boost = booster.get_boost(group_code, jd_text)

        # Get keyword boost for obvious title matches (0.0-0.15 range)
        keyword_boost = _get_keyword_boost(group_code, jd_text)

        # Calculate effective similarity: max of definition or best inclusion
        # This ensures groups with clear inclusions rank higher even if
        # their definition has bureaucratic preamble
        effective_similarity = max(semantic_similarity, best_inclusion_sim)

        # Calculate combined score for ranking
        # Keyword boost helps obvious matches like "Administrative Assistant" -> AS
        combined_score = effective_similarity + labels_boost + keyword_boost

        # Include candidate if:
        # 1. Definition similarity >= min_similarity, OR
        # 2. Best inclusion similarity >= min_similarity (helps IT, etc.)
        if semantic_similarity >= min_similarity or best_inclusion_sim >= min_similarity:
            candidates.append({
                'group': group,
                'semantic_similarity': semantic_similarity,  # Definition sim for LLM
                'inclusion_match': inclusion_match,
                'best_inclusion_sim': best_inclusion_sim,
                'labels_boost': labels_boost,
                'combined_score': combined_score
            })

    # Sort by combined_score descending
    candidates.sort(key=lambda x: x['combined_score'], reverse=True)

    # De-duplicate by group_code - keep only the best-scoring entry per group
    # This prevents groups with many subgroup entries (SRE has 40, SRW has 40)
    # from dominating the shortlist
    seen_codes = set()
    unique_candidates = []
    for candidate in candidates:
        code = candidate['group'].get('group_code', '')
        if code not in seen_codes:
            seen_codes.add(code)
            unique_candidates.append(candidate)

    # Return top max_candidates from de-duplicated list
    return unique_candidates[:max_candidates]


__all__ = ['shortlist_with_all_signals']
