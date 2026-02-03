"""API response models."""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from src.models.noc import (
    SearchResult, EnrichedSearchResult, JDElementData, SourceMetadata,
    EnrichedNOCStatement, NOCHierarchy, ReferenceAttributes
)


class SearchResponse(BaseModel):
    """API response for /api/search endpoint."""
    query: str
    results: List[EnrichedSearchResult]  # Changed from SearchResult
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


class ExclusionItem(BaseModel):
    """A single exclusion item with code and title."""
    code: str
    title: str

    model_config = ConfigDict(from_attributes=True)


class HollandInterest(BaseModel):
    """Holland code interest with title, description, and rank."""
    code: str
    title: str
    description: str
    rank: int

    model_config = ConfigDict(from_attributes=True)


class PersonalAttribute(BaseModel):
    """Personal attribute with name and level."""
    name: str
    level: int

    model_config = ConfigDict(from_attributes=True)


class WorkContextItem(BaseModel):
    """Work context item with name and level."""
    name: str
    level: int

    model_config = ConfigDict(from_attributes=True)


class OtherJobInfo(BaseModel):
    """Additional job information for the Other tab."""
    exclusions: List[ExclusionItem] = Field(default_factory=list)
    employment_requirements: List[str] = Field(default_factory=list)
    workplaces: List[str] = Field(default_factory=list)
    interests: List[HollandInterest] = Field(default_factory=list)
    personal_attributes: List[PersonalAttribute] = Field(default_factory=list)
    work_context_responsibility: List[WorkContextItem] = Field(default_factory=list)
    work_context_effort: List[WorkContextItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    """API response for /api/profile endpoint."""
    noc_code: str
    title: str

    # Example titles / "Also known as"
    example_titles: List[str] = Field(default_factory=list)

    # Labels from NOC 2025 parquet data (for NOC Hierarchy level 6)
    labels: List[str] = Field(default_factory=list)

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

    # Other Job Info (for "Other" tab)
    other_job_info: Optional[OtherJobInfo] = None

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
