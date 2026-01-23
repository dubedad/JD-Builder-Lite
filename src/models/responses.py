"""API response models."""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from src.models.noc import (
    SearchResult, JDElementData, SourceMetadata,
    EnrichedNOCStatement, NOCHierarchy, ReferenceAttributes
)


class SearchResponse(BaseModel):
    """API response for /api/search endpoint."""
    query: str
    results: List[SearchResult]
    count: int
    metadata: SourceMetadata

    model_config = ConfigDict(from_attributes=True)


class EnrichedJDElementData(BaseModel):
    """JD Element with enriched statements and category definition."""
    statements: List[EnrichedNOCStatement]
    category_definition: Optional[str] = None
    source_attribute: str  # "Skills", "Abilities", etc.

    model_config = ConfigDict(from_attributes=True)


class WorkContextData(BaseModel):
    """Work Context split into classified sections."""
    responsibilities: List[EnrichedNOCStatement] = Field(default_factory=list)
    effort: List[EnrichedNOCStatement] = Field(default_factory=list)
    other_work_context: List[EnrichedNOCStatement] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    """API response for /api/profile endpoint."""
    noc_code: str
    title: str

    # NOC hierarchy (DISP-09, DISP-10)
    noc_hierarchy: Optional[NOCHierarchy] = None

    # Enriched JD Elements
    key_activities: EnrichedJDElementData
    skills: EnrichedJDElementData
    effort: EnrichedJDElementData           # From Work Context (DATA-04)
    responsibility: EnrichedJDElementData   # From Work Context (DATA-03)
    working_conditions: EnrichedJDElementData

    # Work Context classified (alternative view)
    work_context: Optional[WorkContextData] = None

    # Reference attributes for Annex (DISP-11)
    reference_attributes: Optional[ReferenceAttributes] = None

    # Provenance
    metadata: SourceMetadata

    # Enrichment metadata
    csv_loaded_at: Optional[str] = None
    enrichment_stats: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """API error response."""
    error: str
    detail: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
