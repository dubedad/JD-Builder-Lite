"""Multi-factor confidence scoring for occupational group matches.

Scoring weights (updated 2026-03-26):
- 50% definition fit     — LLM holistic definition assessment
- 25% semantic similarity — embedding distance to definition text
- 15% inclusion match    — LLM-scored inclusion statement coverage
- 10% labels boost       — labels.csv keyword match

Exclusion conflict: hard-gate 0.3 multiplier penalty (unchanged).
Borderline detection: 10% margin between top scores.
Minimum 0.3 confidence threshold for top-3 recommendations.

Design decision (2026-03-26):
Inclusions are now ACTIVE scoring evidence, weighted at 15%.
Rationale: Many TBS occupational groups (AS, CR, PM, DA, etc.) are
sub-groups of PA and share the same parent definition text. Inclusion
statements are the PRIMARY differentiator between these sub-groups.
Without inclusion scoring, the classifier cannot meaningfully separate
AS from CR from PM — they would all score identically on definition fit.
"""

from typing import Dict, List, Tuple


# Minimum confidence threshold for recommendations
CONFIDENCE_THRESHOLD = 0.3


class ConfidenceCalculator:
    """Calculate calibrated confidence scores from multiple signals.

    Component weights (2026-03-26 rebalance):
    - DEFINITION_FIT:      50% — LLM holistic definition match
    - SEMANTIC_SIMILARITY: 25% — embedding distance to definition text
    - INCLUSION_MATCH:     15% — fraction of inclusion statements that apply
    - LABELS_BOOST:        10% — labels.csv keyword support

    Exclusion conflict: hard-gate 0.3 multiplier (unchanged).

    Previous weights (pre-2026-03-26): 60/30/0/10
    Updated weights:                   50/25/15/10
    """

    # Component weights — must sum to 1.0
    DEFINITION_FIT_WEIGHT = 0.50       # LLM holistic assessment
    SEMANTIC_SIMILARITY_WEIGHT = 0.25  # Embedding similarity to definition
    INCLUSION_MATCH_WEIGHT = 0.15      # Inclusion statement coverage (LLM-scored)
    LABELS_BOOST_WEIGHT = 0.10         # labels.csv support

    def calculate_confidence(
        self,
        definition_fit_score: float,         # 0.0-1.0 from LLM
        semantic_similarity: float,          # 0.0-1.0 from embeddings
        exclusion_conflict: bool,            # Do exclusions apply?
        labels_boost: float,                 # 0.0-0.1 from labels matcher
        inclusion_match_score: float = 0.0,  # 0.0-1.0 from LLM inclusion scoring
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate final confidence and component breakdown.

        Args:
            definition_fit_score: 0.0-1.0 from LLM holistic assessment
            semantic_similarity: 0.0-1.0 from embedding similarity
            exclusion_conflict: True if exclusions apply (hard gate)
            labels_boost: 0.0-0.1 from labels.csv matcher
            inclusion_match_score: 0.0-1.0 fraction of inclusion statements
                that apply to this JD (LLM-scored). Default 0.0 if not provided.

        Returns:
            Tuple of (confidence: float, breakdown: dict)

        Breakdown dict keys:
        - definition_fit: weighted contribution
        - semantic_similarity: weighted contribution
        - inclusion_match: weighted contribution
        - labels_boost: additive contribution
        - exclusion_penalty: penalty applied (if any)
        """
        # Calculate weighted components
        definition_component = definition_fit_score * self.DEFINITION_FIT_WEIGHT
        semantic_component = semantic_similarity * self.SEMANTIC_SIMILARITY_WEIGHT
        inclusion_component = inclusion_match_score * self.INCLUSION_MATCH_WEIGHT
        labels_component = labels_boost * self.LABELS_BOOST_WEIGHT

        base_confidence = (
            definition_component
            + semantic_component
            + inclusion_component
            + labels_component
        )

        # Apply exclusion penalty if conflict detected
        # Hard gate: if primary purpose matches an exclusion, severely penalise
        exclusion_penalty = 0.0
        if exclusion_conflict:
            exclusion_penalty = base_confidence * 0.7  # amount removed
            base_confidence = base_confidence * 0.3    # what remains

        breakdown = {
            "definition_fit": definition_component,
            "semantic_similarity": semantic_component,
            "inclusion_match": inclusion_component,
            "labels_boost": labels_component,
            "exclusion_penalty": exclusion_penalty,
        }

        final_confidence = min(1.0, base_confidence)
        return (final_confidence, breakdown)

    @staticmethod
    def check_borderline(scores: List[float]) -> Tuple[bool, str]:
        """Check if top scores indicate borderline case.

        Flag for expert review when top scores are within 10% of each other.

        Args:
            scores: List of confidence scores (should be sorted descending)

        Returns:
            Tuple of (is_borderline: bool, match_context: str)
        """
        if not scores or len(scores) < 2:
            if scores and scores[0] >= 0.85:
                return (False, "dominant match")
            elif scores and scores[0] >= 0.3:
                return (False, "only viable option")
            else:
                return (False, "low confidence")

        margin = scores[0] - scores[1]
        match_context = ConfidenceCalculator.get_match_context(scores)
        is_borderline = margin < 0.1
        return (is_borderline, match_context)

    @staticmethod
    def get_match_context(scores: List[float]) -> str:
        """Return match context string based on score distribution.

        Args:
            scores: List of confidence scores (should be sorted descending)

        Returns:
            Context string: 'dominant match' | 'competitive field' |
                            'borderline - needs review' | 'only viable option' |
                            'low confidence' | 'no viable candidates'
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
    inclusion_match_score: float = 0.0,
) -> Tuple[float, Dict[str, float]]:
    """Convenience function for calculating confidence.

    Args:
        definition_fit_score: 0.0-1.0 from LLM holistic assessment
        semantic_similarity: 0.0-1.0 from embedding similarity
        exclusion_conflict: True if exclusions apply
        labels_boost: 0.0-0.1 from labels.csv matcher
        inclusion_match_score: 0.0-1.0 inclusion coverage (default 0.0)

    Returns:
        Tuple of (confidence: float, breakdown: dict)
    """
    calc = ConfidenceCalculator()
    return calc.calculate_confidence(
        definition_fit_score, semantic_similarity, exclusion_conflict,
        labels_boost, inclusion_match_score
    )


def check_borderline(scores: List[float]) -> Tuple[bool, str]:
    """Convenience function for borderline detection.

    Args:
        scores: List of confidence scores (should be sorted descending)

    Returns:
        Tuple of (is_borderline: bool, match_context: str)
    """
    return ConfidenceCalculator.check_borderline(scores)
