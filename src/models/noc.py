"""NOC data models with provenance metadata."""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class SourceMetadata(BaseModel):
    """Provenance tracking for scraped data."""
    noc_code: str
    profile_url: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "2025.0"

    model_config = ConfigDict(from_attributes=True)


class SearchResult(BaseModel):
    """Single search result from OASIS."""
    noc_code: str
    title: str
    url: str

    model_config = ConfigDict(from_attributes=True)


class NOCStatement(BaseModel):
    """Single statement from NOC profile with source tracking."""
    text: str
    source_attribute: str  # e.g. "Main Duties", "Skills"
    source_url: str

    model_config = ConfigDict(from_attributes=True)


class JDElementData(BaseModel):
    """Data for a single JD element (e.g., Key Activities)."""
    statements: List[NOCStatement]

    model_config = ConfigDict(from_attributes=True)


class EnrichmentSource(str, Enum):
    """Source of enrichment data."""
    GUIDE_CSV = "guide_csv"
    LLM_IMPUTED = "llm_imputed"


class ProficiencyLevel(BaseModel):
    """Proficiency level with scale context."""
    level: int
    max: int
    label: str
    dimension: str  # "Proficiency", "Complexity", "Frequency", etc.

    model_config = ConfigDict(from_attributes=True)


class EnrichedNOCStatement(BaseModel):
    """NOC statement with enrichment metadata."""
    # Original fields
    text: str
    source_attribute: str
    source_url: str

    # Enrichment fields
    element_id: Optional[str] = None
    description: Optional[str] = None
    proficiency: Optional[ProficiencyLevel] = None
    category_definition: Optional[str] = None
    dimension_type: Optional[str] = None  # For Work Context
    classification: Optional[str] = None  # "responsibilities", "effort", "other_work_context"
    classification_reason: Optional[str] = None

    # Metadata
    enrichment_source: Optional[EnrichmentSource] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)


# NOC 2021 Broad Occupational Categories
BROAD_CATEGORIES = {
    0: "Legislative and senior management occupations",
    1: "Business, finance and administration occupations",
    2: "Natural and applied sciences and related occupations",
    3: "Health occupations",
    4: "Occupations in education, law, social, community and government services",
    5: "Occupations in art, culture, recreation and sport",
    6: "Sales and service occupations",
    7: "Trades, transport and equipment operators and related occupations",
    8: "Natural resources, agriculture and related production occupations",
    9: "Occupations in manufacturing and utilities"
}


class NOCHierarchy(BaseModel):
    """NOC code hierarchy breakdown."""
    noc_code: str
    broad_category: int          # First digit (0-9)
    broad_category_name: str     # From NOC 2021 categories
    teer_category: int           # Second digit (0-5)
    teer_description: str        # From TEER_CATEGORIES
    major_group: str             # First 2 digits
    minor_group: str             # First 3 digits
    unit_group: str              # First 4 digits

    model_config = ConfigDict(from_attributes=True)


class Interest(BaseModel):
    """OASIS interest with description."""
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CareerMobilityPath(BaseModel):
    """Career mobility path with NOC code reference."""
    title: str
    noc_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobRequirements(BaseModel):
    """Structured job requirements by type."""
    education: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    licenses: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    other: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ReferenceAttributes(BaseModel):
    """Reference NOC attributes for Annex section."""
    example_titles: List[str] = Field(default_factory=list)
    interests: List[Interest] = Field(default_factory=list)
    career_mobility: List[CareerMobilityPath] = Field(default_factory=list)
    job_requirements: Optional[JobRequirements] = None
    personal_attributes: List[str] = Field(default_factory=list)
    core_competencies: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
