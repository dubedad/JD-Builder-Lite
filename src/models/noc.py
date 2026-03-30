"""NOC data models with provenance metadata."""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional
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


class EnrichedSearchResult(BaseModel):
    """Enhanced search result with card data for OaSIS-style display.

    Contains all 6 data points for card view (DISP-20):
    1. lead_statement - from OaSIS card
    2. example_titles - (requires profile fetch, optional)
    3. teer_description - from OaSIS card
    4. mobility_progression - (requires profile fetch, optional)
    5. source_table - (requires profile fetch, optional)
    6. publication_date - (requires profile fetch, optional)

    Plus fields for filtering (DISP-22) and grid view (DISP-21).

    Note: Fields marked "requires profile fetch" are populated as None in this phase.
    Profile data population deferred to Phase 08-C or future enhancement.
    """
    # Core fields (same as SearchResult)
    noc_code: str
    title: str
    url: str

    # Card View Data (from OaSIS search HTML)
    lead_statement: Optional[str] = None
    teer_description: Optional[str] = None
    broad_category_name: Optional[str] = None
    matching_criteria: Optional[str] = None

    # Card View Data (requires profile fetch - optional)
    example_titles: Optional[str] = None
    mobility_progression: Optional[str] = None
    source_table: Optional[str] = None
    publication_date: Optional[str] = None

    # Match source label for badge display (v5.1 SRCH-04)
    source_label: Optional[str] = None  # e.g., "O*NET SOC", "2021 NOC"

    # For Filtering (DISP-22) - derived from NOC code
    broad_category: Optional[int] = None  # First digit of NOC code
    sub_major_group: Optional[str] = None     # First 3 digits (for hierarchy display)
    minor_group: Optional[str] = None     # First 3 digits (legacy name, same as sub_major_group)
    minor_group_name: Optional[str] = None  # Not available from search HTML
    unit_group: Optional[str] = None      # First 4 digits

    # OCHRO Job Architecture fields (from job_architecture.parquet)
    job_function: Optional[str] = None    # primary job function (first match, kept for compat)
    job_family: Optional[str] = None      # primary job family (first match, kept for compat)
    managerial_levels: Optional[List[str]] = None   # all unique managerial levels for this NOC
    ochro_entries: Optional[List[Dict[str, str]]] = None  # all unique [{function, family}] pairs

    # For Grid View (DISP-21) - requires profile fetch
    top_skills: Optional[List[str]] = None
    top_abilities: Optional[List[str]] = None
    top_knowledge: Optional[List[str]] = None

    # Relevance scoring (SRCH-13) - set by API route based on query match location
    relevance_score: Optional[int] = None   # 3=title, 2=lead statement, 1=alternate title
    match_reason: Optional[str] = None      # Human-readable label

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
    major_group_name: Optional[str] = None  # From OASIS HTML
    minor_group: str             # First 3 digits (sub-major in NOC 2021 terms)
    minor_group_name: Optional[str] = None  # From OASIS HTML
    unit_group: str              # First 4 digits (minor in NOC 2021 terms)
    unit_group_name: Optional[str] = None   # From OASIS HTML

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
    lead_statement: Optional[str] = None
    example_titles: List[str] = Field(default_factory=list)
    interests: List[Interest] = Field(default_factory=list)
    career_mobility: List[CareerMobilityPath] = Field(default_factory=list)
    job_requirements: Optional[JobRequirements] = None
    personal_attributes: List[str] = Field(default_factory=list)
    core_competencies: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
