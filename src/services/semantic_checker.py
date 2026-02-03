"""Semantic similarity checker for styled content validation.

This module provides semantic equivalence checking between original NOC statements
and their styled variants using sentence embeddings. Uses the all-MiniLM-L6-v2 model
which is lightweight (22MB), fast, and achieves ~84% accuracy on STS benchmarks.

The 0.75 similarity threshold is intentionally conservative to avoid rejecting
valid paraphrases. Per RESEARCH.md: "higher thresholds reject valid paraphrases"
since the model accuracy is ~84%. Start conservative; tune based on fallback rate.

Used by: GenerationService for post-generation validation (Phase 12)
"""

from typing import Dict, Optional

from sentence_transformers import SentenceTransformer, util


# Threshold per research: 0.75-0.85 range, use 0.75 for conservative acceptance
# all-MiniLM-L6-v2 achieves ~84% accuracy on STS benchmarks; higher thresholds
# would reject valid paraphrases. Monitor fallback rate to tune:
# - If >30% fallback, lower threshold to 0.70
# - If <5%, can raise to 0.80
SEMANTIC_SIMILARITY_THRESHOLD = 0.75


class SemanticChecker:
    """Semantic similarity checker using sentence-transformers.

    Uses the all-MiniLM-L6-v2 model for fast, efficient semantic comparison.
    Model is loaded lazily on first use to avoid blocking app startup.

    Attributes:
        model: SentenceTransformer model (loaded on first use)
        threshold: Similarity threshold for equivalence (default 0.75)
    """

    def __init__(self, threshold: float = SEMANTIC_SIMILARITY_THRESHOLD) -> None:
        """Initialize semantic checker.

        Args:
            threshold: Minimum cosine similarity for equivalence (default 0.75)
        """
        self._model: Optional[SentenceTransformer] = None
        self.threshold = threshold

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the sentence transformer model.

        Model is loaded on first access to avoid blocking app startup.
        all-MiniLM-L6-v2 is 22MB, loads in ~1-2 seconds on first use.

        Returns:
            Loaded SentenceTransformer model
        """
        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def check_equivalence(self, original: str, styled: str) -> Dict:
        """Check if styled text preserves original meaning.

        Computes cosine similarity between sentence embeddings of original
        and styled text. Returns equivalence status based on threshold.

        Args:
            original: Original NOC statement
            styled: Styled variant to validate

        Returns:
            Dict with:
                - is_equivalent: bool (similarity >= threshold)
                - similarity_score: float (0-1, rounded to 4 decimals)
                - threshold: float (configured threshold)
        """
        # Encode both texts to embeddings (384-dimensional vectors)
        embeddings = self.model.encode(
            [original, styled],
            convert_to_tensor=True
        )

        # Compute cosine similarity (default metric for sentence-transformers)
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

        return {
            "is_equivalent": similarity >= self.threshold,
            "similarity_score": round(similarity, 4),
            "threshold": self.threshold
        }


# Module-level singleton for convenience
_semantic_checker: Optional[SemanticChecker] = None


def check_semantic_equivalence(original: str, styled: str) -> Dict:
    """Check semantic equivalence using singleton checker instance.

    Convenience function that manages a singleton SemanticChecker instance.
    Model is loaded lazily on first call.

    Args:
        original: Original NOC statement
        styled: Styled variant to validate

    Returns:
        Dict with is_equivalent, similarity_score, threshold
    """
    global _semantic_checker
    if _semantic_checker is None:
        _semantic_checker = SemanticChecker()
    return _semantic_checker.check_equivalence(original, styled)
