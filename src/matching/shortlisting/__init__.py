"""Shortlisting module for pre-filtering candidate occupational groups.

This module provides semantic similarity matching and labels-based confidence boost
to reduce token costs and improve LLM focus by identifying viable candidates before
expensive LLM classification.

Per CONTEXT.md: "Hybrid approach - match all groups but boost confidence if labels.csv
supports the match"
"""

from typing import List, Dict

# Lazy imports to avoid loading heavy models unless needed
_semantic_matcher = None
_labels_booster = None


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
    1. Semantic similarity to DEFINITION - primary ranking signal
    2. Semantic similarity to INCLUSIONS - used for FILTERING only, not scoring
       (a group with inclusion match passes shortlist even if definition similarity is borderline)
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
            'semantic_similarity': float,  # similarity to definition
            'inclusion_match': bool,       # True if inclusions helped shortlist
            'labels_boost': float,
            'combined_score': float        # definition_similarity + labels_boost ONLY
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

        # Check if inclusions help shortlist (filtering role only)
        inclusion_match = False
        inclusions = group.get('inclusions', [])
        if inclusions and isinstance(inclusions, list):
            # Check if any inclusion has high semantic similarity to JD text
            # This helps shortlist candidates with borderline definition matches
            for inclusion in inclusions:
                if isinstance(inclusion, str):
                    inclusion_sim = matcher.compute_similarity(jd_text, inclusion)
                    # If inclusion matches well (>0.5), flag as inclusion_match
                    if inclusion_sim >= 0.5:
                        inclusion_match = True
                        break

        # Get labels boost (0.0-0.1 range)
        group_code = group.get('group_code', '')
        labels_boost = booster.get_boost(group_code, jd_text)

        # Calculate combined score (definition + labels ONLY, NOT inclusions)
        combined_score = semantic_similarity + labels_boost

        # Include candidate if:
        # 1. Definition similarity >= min_similarity, OR
        # 2. Inclusion match helps shortlist (even if definition is borderline)
        if semantic_similarity >= min_similarity or (inclusion_match and semantic_similarity >= min_similarity * 0.7):
            candidates.append({
                'group': group,
                'semantic_similarity': semantic_similarity,
                'inclusion_match': inclusion_match,
                'labels_boost': labels_boost,
                'combined_score': combined_score
            })

    # Sort by combined_score descending
    candidates.sort(key=lambda x: x['combined_score'], reverse=True)

    # Return top max_candidates
    return candidates[:max_candidates]


__all__ = ['shortlist_with_all_signals']
