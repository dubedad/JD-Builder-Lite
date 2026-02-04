"""Multi-factor confidence scoring for occupational group matches.

Per CONTEXT.md decisions:
- Multi-factor confidence: 60% definition fit, 30% semantic, 10% labels
- NO inclusion weight (inclusions for shortlisting only, not scoring)
- Exclusion conflict applies 0.3 multiplier penalty
- Borderline detection at 10% margin between top scores
- Minimum 0.3 confidence threshold for top-3 recommendations
"""

from typing import Dict, List, Tuple


# Minimum confidence threshold for recommendations
CONFIDENCE_THRESHOLD = 0.3


class ConfidenceCalculator:
    """Calculate calibrated confidence scores from multiple signals.

    Per CONTEXT.md:
    - High confidence (0.85+): Multi-factor match
    - Show component breakdown for transparency
    - Flag borderline when top scores within 10%

    IMPORTANT per CONTEXT.md decision:
    "Inclusion statements: Use for shortlisting candidates only, not for scoring or evidence"

    Therefore, inclusions are NOT part of confidence calculation.
    """

    # Component weights (must sum to 1.0)
    # NOTE: No INCLUSION_SUPPORT_WEIGHT - inclusions used for shortlisting only
    DEFINITION_FIT_WEIGHT = 0.60  # LLM holistic assessment
    SEMANTIC_SIMILARITY_WEIGHT = 0.30  # Embedding similarity to definition
    LABELS_BOOST_WEIGHT = 0.10  # labels.csv support

    def calculate_confidence(
        self,
        definition_fit_score: float,  # 0.0-1.0 from LLM
        semantic_similarity: float,  # 0.0-1.0 from embeddings
        exclusion_conflict: bool,  # Do exclusions apply?
        labels_boost: float,  # 0.0-0.1 from labels matcher
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate final confidence and component breakdown.

        NOTE: inclusion_match is NOT a parameter here.
        Per CONTEXT.md: "Inclusion statements: Use for shortlisting candidates only"
        Inclusions help identify candidates in Plan 15-02, but do NOT boost confidence.

        Args:
            definition_fit_score: 0.0-1.0 from LLM holistic assessment
            semantic_similarity: 0.0-1.0 from embedding similarity
            exclusion_conflict: True if exclusions apply (hard gate)
            labels_boost: 0.0-0.1 from labels.csv matcher

        Returns:
            Tuple of (confidence: float, breakdown: dict)

        Breakdown dict keys:
        - definition_fit: weighted contribution
        - semantic_similarity: weighted contribution
        - labels_boost: additive contribution
        - exclusion_penalty: penalty applied (if any)
        """
        # Calculate weighted components
        definition_component = definition_fit_score * self.DEFINITION_FIT_WEIGHT
        semantic_component = semantic_similarity * self.SEMANTIC_SIMILARITY_WEIGHT
        labels_component = labels_boost * self.LABELS_BOOST_WEIGHT

        # Base confidence (no inclusion component per user decision)
        base_confidence = definition_component + semantic_component + labels_component

        # Apply exclusion penalty if conflict detected
        exclusion_penalty = 0.0
        if exclusion_conflict:
            # Per CONTEXT.md: "Hard gate - if primary purpose matches exclusion, eliminate group"
            # Severe penalty: multiply by 0.3
            exclusion_penalty = base_confidence * 0.7  # Amount removed
            base_confidence = base_confidence * 0.3  # What remains

        breakdown = {
            "definition_fit": definition_component,
            "semantic_similarity": semantic_component,
            "labels_boost": labels_component,
            "exclusion_penalty": exclusion_penalty,
        }

        # Cap at 1.0
        final_confidence = min(1.0, base_confidence)

        return (final_confidence, breakdown)

    @staticmethod
    def check_borderline(scores: List[float]) -> Tuple[bool, str]:
        """Check if top scores indicate borderline case.

        Per CONTEXT.md: "Flag for expert review when top scores within 10%"

        Args:
            scores: List of confidence scores (should be sorted descending)

        Returns:
            Tuple of (is_borderline: bool, match_context: str)

        match_context values:
        - "dominant match" if margin > 0.3
        - "competitive field" if margin 0.1-0.3
        - "borderline - needs review" if margin < 0.1
        """
        if not scores or len(scores) < 2:
            # Only one candidate or no candidates - not borderline
            if scores and scores[0] >= 0.85:
                return (False, "dominant match")
            elif scores and scores[0] >= 0.3:
                return (False, "only viable option")
            else:
                return (False, "low confidence")

        # Calculate margin between top two scores
        margin = scores[0] - scores[1]

        # Determine match context
        match_context = ConfidenceCalculator.get_match_context(scores)

        # Borderline if margin < 0.1 (within 10%)
        is_borderline = margin < 0.1

        return (is_borderline, match_context)

    @staticmethod
    def get_match_context(scores: List[float]) -> str:
        """Return match context string based on score distribution.

        Args:
            scores: List of confidence scores (should be sorted descending)

        Returns:
            Context string describing the match situation
        """
        if not scores:
            return "no viable candidates"

        if len(scores) == 1:
            if scores[0] >= 0.85:
                return "dominant match"
            elif scores[0] >= 0.3:
                return "only viable option"
            else:
                return "low confidence"

        # Multiple scores - check margin
        margin = scores[0] - scores[1]

        if margin > 0.3:
            return "dominant match"
        elif margin >= 0.1:
            return "competitive field"
        else:
            return "borderline - needs review"


def calculate_confidence(
    definition_fit_score: float,
    semantic_similarity: float,
    exclusion_conflict: bool,
    labels_boost: float,
) -> Tuple[float, Dict[str, float]]:
    """Convenience function for calculating confidence.

    Wraps ConfidenceCalculator.calculate_confidence() for simple usage.

    Args:
        definition_fit_score: 0.0-1.0 from LLM holistic assessment
        semantic_similarity: 0.0-1.0 from embedding similarity
        exclusion_conflict: True if exclusions apply
        labels_boost: 0.0-0.1 from labels.csv matcher

    Returns:
        Tuple of (confidence: float, breakdown: dict)
    """
    calc = ConfidenceCalculator()
    return calc.calculate_confidence(
        definition_fit_score, semantic_similarity, exclusion_conflict, labels_boost
    )


def check_borderline(scores: List[float]) -> Tuple[bool, str]:
    """Convenience function for borderline detection.

    Wraps ConfidenceCalculator.check_borderline() for simple usage.

    Args:
        scores: List of confidence scores (should be sorted descending)

    Returns:
        Tuple of (is_borderline: bool, match_context: str)
    """
    return ConfidenceCalculator.check_borderline(scores)
