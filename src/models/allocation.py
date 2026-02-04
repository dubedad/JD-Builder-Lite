"""API request/response models for POST /api/allocate endpoint.

These models define the contract between frontend and backend for
occupational group allocation, ensuring type safety, validation,
and documentation.
"""

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field, field_validator

from src.matching.models import GroupRecommendation

__all__ = [
    "AllocationRequest",
    "AllocationResponse",
    "ProvenanceDetail",
    "AllocationStatus",
    "ALLOCATION_STATUS_SUCCESS",
    "ALLOCATION_STATUS_NEEDS_CLARIFICATION",
    "ALLOCATION_STATUS_INVALID_COMBINATION",
]

# Type alias for status strings
AllocationStatus = Literal["success", "needs_clarification", "invalid_combination"]

# Status constants for programmatic use
ALLOCATION_STATUS_SUCCESS = "success"
ALLOCATION_STATUS_NEEDS_CLARIFICATION = "needs_clarification"
ALLOCATION_STATUS_INVALID_COMBINATION = "invalid_combination"


class AllocationRequest(BaseModel):
    """Request model for POST /api/allocate.

    Requires complete JD with Client-Service Results and Key Activities filled in.
    Per CONTEXT.md: Single JD per request, no batch support, no auth required.
    """
    position_title: str = Field(
        min_length=1,
        description="Job position title"
    )
    client_service_results: str = Field(
        min_length=10,
        description="Primary purpose statement - why this position exists"
    )
    key_activities: List[str] = Field(
        min_length=1,
        description="List of key activities (at least 1 required)"
    )
    skills: Optional[List[str]] = Field(
        default=None,
        description="Optional skills list from JD"
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="NOC labels for confidence boost"
    )
    minimum_confidence: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for recommendations"
    )

    @field_validator("client_service_results")
    @classmethod
    def validate_client_service_results(cls, v: str) -> str:
        """Ensure Client-Service Results has substantive content."""
        if len(v.strip()) < 10:
            raise ValueError("Client-Service Results must have at least 10 characters of content")
        return v.strip()

    @field_validator("key_activities")
    @classmethod
    def validate_key_activities(cls, v: List[str]) -> List[str]:
        """Ensure at least 1 non-empty key activity."""
        non_empty = [ka.strip() for ka in v if ka.strip()]
        if not non_empty:
            raise ValueError("At least 1 non-empty Key Activity is required")
        return non_empty


class ProvenanceDetail(BaseModel):
    """Provenance information for a single group recommendation.

    Per CONTEXT.md: Provenance links embedded in each recommendation.
    Structure kept to 2 levels per RESEARCH.md (avoid >3 nesting).
    """
    source_type: str = Field(
        default="TBS Occupational Group Definition",
        description="Type of authoritative source"
    )
    url: str = Field(description="TBS source URL for this group's definition")
    definition_paragraph: str = Field(
        default="Definition",
        description="Which paragraph of the definition was referenced"
    )
    inclusions_referenced: List[str] = Field(
        default_factory=list,
        description="Inclusion paragraph labels (I1, I2, etc.) that support match"
    )
    exclusions_checked: List[str] = Field(
        default_factory=list,
        description="Exclusion paragraph labels (E1, E2, etc.) that were verified"
    )
    scraped_at: str = Field(description="ISO timestamp when TBS page was scraped")
    archive_path: Optional[str] = Field(
        default=None,
        description="Path to archived HTML for audit verification"
    )
    data_source_id: int = Field(description="FK to scrape_provenance for full audit trail")


class AllocationResponse(BaseModel):
    """Response model for POST /api/allocate.

    Per CONTEXT.md:
    - Return ranked list of top-3 recommendations as array ordered by confidence
    - Each recommendation includes: group_code, group_name, confidence, rationale
    - Full detailed rationale always included with all evidence inline
    - Provenance links embedded in each recommendation
    - Evidence references use field references AND character offsets

    Per CONTEXT.md error handling:
    - "Needs Work Description Clarification" returns HTTP 200 with status flag
    - "Invalid Combination of Work" returns HTTP 200 with status flag
    """
    status: AllocationStatus = Field(
        description="success | needs_clarification | invalid_combination"
    )
    recommendations: List[GroupRecommendation] = Field(
        max_length=3,
        description="Top 1-3 group recommendations, ranked by confidence"
    )
    provenance_map: Dict[str, ProvenanceDetail] = Field(
        description="Provenance keyed by group_code for each recommendation"
    )
    primary_purpose_summary: str = Field(
        description="Extracted primary purpose from JD"
    )
    match_context: str = Field(
        description="Match quality: 'dominant match' | 'competitive field' | 'borderline' | 'split duties detected'"
    )
    borderline_flag: bool = Field(
        description="True if top scores within 10% (needs expert review)"
    )
    confidence_summary: Dict[str, float] = Field(
        description="Quick lookup: {group_code: confidence} for all recommendations"
    )

    # Edge case fields (populated when status != "success")
    clarification_needed: Optional[List[str]] = Field(
        default=None,
        description="Fields needing more detail when status='needs_clarification'"
    )
    conflicting_duties: Optional[Dict[str, float]] = Field(
        default=None,
        description="Duty distribution when status='invalid_combination'"
    )
    warnings: Optional[List[str]] = Field(
        default=None,
        description="Non-fatal warnings (title-duty mismatch, etc.)"
    )
    constraints_compliance: str = Field(
        default="Evaluated work described in JD, not person-specific attributes",
        description="TBS constraint confirmation"
    )
