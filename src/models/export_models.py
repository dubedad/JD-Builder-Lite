"""Export models for PDF and Word document generation."""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from email.utils import parsedate_to_datetime


def parse_flexible_datetime(value):
    """Parse datetime from ISO 8601 or RFC 2822 format."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Try RFC 2822 first (e.g., 'Thu, 22 Jan 2026 09:31:53 GMT')
        # These typically start with day-of-week abbreviation
        if value and value[0].isalpha():
            try:
                return parsedate_to_datetime(value)
            except (ValueError, TypeError):
                pass
        # Try ISO 8601 (e.g., '2026-01-22T09:31:53Z')
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            pass
        # Last resort: try RFC 2822 anyway
        try:
            return parsedate_to_datetime(value)
        except (ValueError, TypeError):
            pass
    raise ValueError(f"Cannot parse datetime: {value}")


class SelectionMetadata(BaseModel):
    """Manager's selection with audit trail data."""
    id: str  # e.g., "key_activities-0"
    text: str
    jd_element: str  # "key_activities", "skills", etc.
    source_attribute: str  # NOC attribute name (e.g., "Main Duties")
    source_url: str
    selected_at: datetime  # When manager selected (for Directive 6.2.7)

    model_config = ConfigDict(from_attributes=True)

    @field_validator('selected_at', mode='before')
    @classmethod
    def parse_selected_at(cls, v):
        return parse_flexible_datetime(v)


class AIMetadata(BaseModel):
    """AI-generated content disclosure for Directive compliance."""
    model: str  # e.g., "gpt-4o"
    timestamp: datetime
    prompt_version: str
    input_statement_ids: List[str]
    modified: bool = False  # True if manager edited output

    model_config = ConfigDict(from_attributes=True)

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        return parse_flexible_datetime(v)


class SourceMetadataExport(BaseModel):
    """NOC source metadata for compliance appendix."""
    noc_code: str
    profile_url: str
    scraped_at: datetime
    version: str  # NOC version (e.g., "2025.0")

    model_config = ConfigDict(from_attributes=True)

    @field_validator('scraped_at', mode='before')
    @classmethod
    def parse_scraped_at(cls, v):
        return parse_flexible_datetime(v)


class ExportRequest(BaseModel):
    """Request body for export endpoints."""
    noc_code: str
    job_title: str
    general_overview: Optional[str] = None
    selections: List[SelectionMetadata]
    ai_metadata: Optional[AIMetadata] = None
    source_metadata: SourceMetadataExport

    model_config = ConfigDict(from_attributes=True)


class JDElementExport(BaseModel):
    """JD Element section for export."""
    name: str  # Display name (e.g., "Key Activities")
    key: str  # Internal key (e.g., "key_activities")
    statements: List[str]

    model_config = ConfigDict(from_attributes=True)


class ComplianceSection(BaseModel):
    """Compliance appendix section."""
    section_id: str  # Directive section (e.g., "6.2.7")
    title: str
    content: Dict[str, Any]  # Flexible structure per section

    model_config = ConfigDict(from_attributes=True)


class AnnexSection(BaseModel):
    """Single Annex category section for unused NOC attributes."""
    title: str  # Display title: "Job Requirements", "Career Mobility", etc.
    category: str  # Internal key: job_requirements, career_mobility, interests, personal_suitability
    items: List[str]  # Content items for this section
    format_type: Literal['paragraph', 'list', 'grouped_list']

    model_config = ConfigDict(from_attributes=True)


class AnnexData(BaseModel):
    """Complete Annex section data with all categories."""
    sections: List[AnnexSection]
    source_noc_code: str
    retrieved_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator('retrieved_at', mode='before')
    @classmethod
    def parse_retrieved_at(cls, v):
        return parse_flexible_datetime(v)


class ExportData(BaseModel):
    """Complete data structure for PDF/Word template rendering."""
    # Header info
    noc_code: str
    job_title: str

    # Main content
    general_overview: Optional[str] = None
    jd_elements: List[JDElementExport]

    # Compliance metadata
    manager_selections: List[SelectionMetadata]
    ai_metadata: Optional[AIMetadata] = None
    source_metadata: SourceMetadataExport
    compliance_sections: List[ComplianceSection]

    # Annex section (unused NOC attributes)
    annex_data: Optional[AnnexData] = None

    # Export metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
