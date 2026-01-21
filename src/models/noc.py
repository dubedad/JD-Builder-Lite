"""NOC data models with provenance metadata."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List
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
