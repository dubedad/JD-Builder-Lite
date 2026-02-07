"""Export models for PDF and Word document generation."""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any, Literal, TYPE_CHECKING
from datetime import datetime
from email.utils import parsedate_to_datetime

from src.models.ai import StyleContentType
from src.models.vocabulary_audit import CONFIDENCE_THRESHOLDS

if TYPE_CHECKING:
    from src.models.styled_content import StyledStatement


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


class ProficiencyData(BaseModel):
    """Proficiency/importance level for a statement."""
    level: Optional[int] = None  # 1-5 scale
    max: int = 5
    label: Optional[str] = None  # e.g., "High Level"

    model_config = ConfigDict(from_attributes=True)


class StyledStatementExport(BaseModel):
    """Styled statement data for export templates.

    Captures styled content display data for PDF/DOCX exports with
    confidence level mapping for visual indicators.

    Attributes:
        styled_text: The AI-styled text variant
        original_noc_text: Preserved original NOC text for audit
        content_type: AI disclosure type (AI_STYLED, ORIGINAL_NOC, etc.)
        confidence_score: AI confidence in styling quality (0.0-1.0)
        confidence_level: "high", "medium", "low" for CSS class mapping
        vocabulary_coverage: Percentage of content using NOC vocabulary
        disclosure_label: Human-readable disclosure label for compliance
    """
    styled_text: str
    original_noc_text: str
    content_type: StyleContentType
    confidence_score: float
    confidence_level: str  # "high", "medium", "low" for CSS class
    vocabulary_coverage: float
    disclosure_label: str

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_styled_statement(cls, stmt: "StyledStatement") -> "StyledStatementExport":
        """Factory from StyledStatement model.

        Maps confidence score to level using thresholds from vocabulary_audit.py
        and content type to disclosure labels for compliance appendix.

        Args:
            stmt: StyledStatement object from generation

        Returns:
            StyledStatementExport ready for template rendering
        """
        # Map confidence score to level
        if stmt.confidence_score >= CONFIDENCE_THRESHOLDS["high"]:
            level = "high"
        elif stmt.confidence_score >= CONFIDENCE_THRESHOLDS["medium"]:
            level = "medium"
        else:
            level = "low"

        # Map content type to disclosure label
        labels = {
            StyleContentType.AI_STYLED: "AI-Styled using Job Description Samples",
            StyleContentType.AI_GENERATED: "AI-Generated",
            StyleContentType.ORIGINAL_NOC: "Original NOC",
        }

        return cls(
            styled_text=stmt.styled_text,
            original_noc_text=stmt.original_noc_text,
            content_type=stmt.content_type,
            confidence_score=stmt.confidence_score,
            confidence_level=level,
            vocabulary_coverage=stmt.vocabulary_coverage,
            disclosure_label=labels.get(stmt.content_type, "Unknown")
        )


class SelectionMetadata(BaseModel):
    """Manager's selection with audit trail data."""
    id: str  # e.g., "key_activities-0"
    text: str
    jd_element: str  # "key_activities", "skills", etc.
    source_attribute: str  # NOC attribute name (e.g., "Main Duties")
    source_url: Optional[str] = None
    selected_at: datetime  # When manager selected (for Directive 6.2.7)
    description: Optional[str] = None  # Element description from guide.csv
    proficiency: Optional[ProficiencyData] = None  # Importance/proficiency level
    publication_date: Optional[str] = None  # OaSIS table publication date (e.g., "2025-10-30")
    source_table_url: Optional[str] = None  # URL to OaSIS table on open.canada.ca

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
    classification_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Classification allocation response to include in export"
    )
    include_classification: bool = Field(
        default=False,
        description="Whether to include classification section in export"
    )

    model_config = ConfigDict(from_attributes=True)


class StatementExport(BaseModel):
    """Individual statement for export with full metadata."""
    text: str
    source_attribute: str  # e.g., "Main Duties", "Skills"
    description: Optional[str] = None  # Element description from guide.csv
    proficiency: Optional[ProficiencyData] = None  # Importance/proficiency level
    publication_date: Optional[str] = None  # OaSIS table publication date
    source_table_url: Optional[str] = None  # URL to OaSIS table on open.canada.ca
    # Optional styled variant for dual-format display in exports
    styled_variant: Optional[StyledStatementExport] = None

    model_config = ConfigDict(from_attributes=True)


class JDElementExport(BaseModel):
    """JD Element section for export."""
    name: str  # Display name (e.g., "Key Activities")
    key: str  # Internal key (e.g., "key_activities")
    statements: List[StatementExport]  # Structured statements with metadata

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

    # Classification results
    classification_result: Optional[Dict[str, Any]] = None
    include_classification: bool = False

    # Export metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
