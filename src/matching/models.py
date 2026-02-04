"""Pydantic models for structured LLM classification outputs.

These models define the data contracts for OpenAI structured output,
capturing allocation results with full rationale and provenance.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator


class EvidenceSpan(BaseModel):
    """Single piece of evidence extracted from job description.

    Captures quoted text with field context for provenance.
    """
    text: str = Field(description="Quoted text from job description")
    field: str = Field(description="Source field name, e.g., 'Client-Service Results', 'Key Activity 3'")
    start_char: Optional[int] = Field(
        default=None,
        description="Character position in original text (None if fuzzy matched)"
    )
    end_char: Optional[int] = Field(
        default=None,
        description="End character position in original text"
    )


class ReasoningStep(BaseModel):
    """Chain-of-thought reasoning step in allocation process.

    Captures incremental logic building toward recommendation.
    """
    step_number: int = Field(description="Sequential step number")
    explanation: str = Field(description="What this step determines")
    evidence: str = Field(description="Quoted text supporting this step")
    intermediate_conclusion: str = Field(description="Conclusion reached at this step")


class GroupRecommendation(BaseModel):
    """Single occupational group recommendation with full rationale.

    Captures why this group matches, with confidence breakdown,
    reasoning chain, and TBS policy provenance.
    """
    group_code: str = Field(description="Occupational group code, e.g., 'AI', 'CS', 'PM'")
    group_id: int = Field(description="Foreign key to dim_occupational_group for provenance")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence score 0.0-1.0"
    )
    confidence_breakdown: Dict[str, float] = Field(
        description="Component scores: definition_fit, inclusion_support, exclusion_clear, labels_boost, semantic_similarity"
    )
    definition_fit_rationale: str = Field(
        description="Narrative explanation of how JD matches group definition"
    )
    reasoning_steps: List[ReasoningStep] = Field(
        description="Chain-of-thought reasoning steps",
        default_factory=list
    )
    evidence_spans: List[EvidenceSpan] = Field(
        description="Quoted evidence from JD supporting this recommendation",
        default_factory=list
    )
    inclusion_check: str = Field(
        description="Which inclusion statements support this match, or 'none applies'"
    )
    exclusion_check: str = Field(
        description="Confirmation that exclusion statements do not match"
    )
    provenance_url: str = Field(
        description="TBS source URL for this group's definition"
    )
    provenance_paragraph: Optional[str] = Field(
        default=None,
        description="Specific paragraph label if applicable"
    )


class RejectedGroup(BaseModel):
    """Occupational group that was considered but not recommended.

    Captures why a group was eliminated from consideration.
    """
    group_code: str = Field(description="Occupational group code")
    rejection_reason: str = Field(description="Why this group was eliminated")
    exclusion_conflict: Optional[str] = Field(
        default=None,
        description="Which exclusion statement matched, if applicable"
    )
    confidence_if_considered: float = Field(
        ge=0.0,
        le=1.0,
        description="What confidence score would have been without elimination"
    )


class AllocationResult(BaseModel):
    """Complete occupational group allocation output.

    Top-3 recommendations with rationale, rejected alternatives,
    and match quality indicators for expert review.
    """
    primary_purpose_summary: str = Field(
        description="Extracted primary purpose from job description"
    )
    top_recommendations: List[GroupRecommendation] = Field(
        max_length=3,
        description="Top 1-3 group recommendations, ranked by confidence"
    )
    rejected_groups: List[RejectedGroup] = Field(
        description="Groups considered but not recommended",
        default_factory=list
    )
    borderline_flag: bool = Field(
        description="True if top scores are within 10% (needs expert review)"
    )
    match_context: str = Field(
        description="Match quality indicator: 'dominant match' | 'competitive field' | 'borderline - needs review' | 'split duties detected'"
    )
    constraints_compliance: str = Field(
        default="Evaluated work described in JD, not person-specific attributes",
        description="Confirmation that TBS allocation constraints were followed"
    )
    duty_split: Optional[Dict[str, float]] = Field(
        default=None,
        description="Duty distribution when split detected, e.g., {'AS': 0.4, 'PM': 0.35, 'CS': 0.25}"
    )
    warnings: List[str] = Field(
        description="Warnings about edge cases, e.g., title-duty mismatch",
        default_factory=list
    )

    @field_validator("top_recommendations")
    @classmethod
    def validate_top_recommendations(cls, v: List[GroupRecommendation]) -> List[GroupRecommendation]:
        """Ensure top_recommendations has 1-3 entries."""
        if not v:
            raise ValueError("top_recommendations must have at least 1 entry")
        if len(v) > 3:
            raise ValueError("top_recommendations must have at most 3 entries")
        return v
