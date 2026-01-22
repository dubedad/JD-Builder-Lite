"""Export models for PDF and Word document generation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class SelectionMetadata(BaseModel):
    """Manager's selection with audit trail data."""
    id: str  # e.g., "key_activities-0"
    text: str
    jd_element: str  # "key_activities", "skills", etc.
    source_attribute: str  # NOC attribute name (e.g., "Main Duties")
    source_url: str
    selected_at: datetime  # When manager selected (for Directive 6.2.7)

    model_config = ConfigDict(from_attributes=True)


class AIMetadata(BaseModel):
    """AI-generated content disclosure for Directive compliance."""
    model: str  # e.g., "gpt-4o"
    timestamp: datetime
    prompt_version: str
    input_statement_ids: List[str]
    modified: bool = False  # True if manager edited output

    model_config = ConfigDict(from_attributes=True)


class SourceMetadataExport(BaseModel):
    """NOC source metadata for compliance appendix."""
    noc_code: str
    profile_url: str
    scraped_at: datetime
    version: str  # NOC version (e.g., "2025.0")

    model_config = ConfigDict(from_attributes=True)


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

    # Export metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
