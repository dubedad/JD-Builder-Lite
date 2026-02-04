"""Semantic similarity matcher using sentence-transformers.

Uses all-MiniLM-L6-v2 model: fast, good accuracy, no GPU needed.
Per RESEARCH.md: balanced speed/quality for definition matching.
"""

from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


class SemanticMatcher:
    """Calculate semantic similarity between JD text and occupational group definitions."""

    def __init__(self):
        """Initialize with all-MiniLM-L6-v2 model (fast, good accuracy, no GPU needed)."""
        # Use all-MiniLM-L6-v2: fast, good accuracy, no GPU needed (per RESEARCH.md)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self._definition_cache = {}  # Cache embeddings for group definitions

    def compute_similarity(self, jd_text: str, definition: str) -> float:
        """Calculate cosine similarity between JD and definition.

        Args:
            jd_text: Job description text (combined Client-Service Results + Key Activities)
            definition: Occupational group definition text

        Returns:
            Cosine similarity score between 0.0 and 1.0
        """
        if not jd_text or not definition:
            return 0.0

        # Encode JD text (fresh each time, as JDs are different)
        jd_embedding = self.model.encode(jd_text, convert_to_tensor=True)

        # Check cache for definition embedding
        if definition not in self._definition_cache:
            self._definition_cache[definition] = self.model.encode(
                definition, convert_to_tensor=True
            )

        definition_embedding = self._definition_cache[definition]

        # Calculate cosine similarity
        similarity = cos_sim(jd_embedding, definition_embedding)

        # Extract scalar value (cos_sim returns tensor)
        return float(similarity.item())

    def shortlist_by_definition(
        self,
        jd_text: str,
        groups: List[Dict],
        min_similarity: float = 0.3
    ) -> List[Dict]:
        """
        Return groups with semantic similarity >= threshold.

        Per CONTEXT.md: "Inclusion statements: Use for shortlisting candidates only,
        not for scoring or evidence"

        This method computes similarity to DEFINITION only (not inclusions).
        The combined_score is 100% definition-based.

        Args:
            jd_text: Combined Client-Service Results + Key Activities text
            groups: List of group dicts with 'definition' key
            min_similarity: Threshold (default 0.3 per CONTEXT.md)

        Returns:
            List of dicts with: group, semantic_similarity, ranked by similarity desc
        """
        candidates = []

        for group in groups:
            definition = group.get('definition', '')
            if not definition:
                continue

            similarity = self.compute_similarity(jd_text, definition)

            if similarity >= min_similarity:
                candidates.append({
                    'group': group,
                    'semantic_similarity': similarity
                })

        # Sort by semantic_similarity descending
        candidates.sort(key=lambda x: x['semantic_similarity'], reverse=True)

        return candidates


def shortlist_candidates(
    jd_text: str,
    groups: List[Dict],
    min_similarity: float = 0.3,
    max_candidates: int = 10
) -> List[Dict]:
    """
    Convenience function to shortlist top candidates using semantic similarity.

    Args:
        jd_text: Combined Client-Service Results + Key Activities text
        groups: List of group dicts with 'definition' key
        min_similarity: Threshold (default 0.3 per CONTEXT.md)
        max_candidates: Max candidates to return (default 10)

    Returns:
        List of dicts with: group, semantic_similarity
        Sorted by semantic_similarity desc, limited to max_candidates
    """
    matcher = SemanticMatcher()
    candidates = matcher.shortlist_by_definition(jd_text, groups, min_similarity)
    return candidates[:max_candidates]


__all__ = ['SemanticMatcher', 'shortlist_candidates']
