"""API response models."""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from src.models.noc import SearchResult, JDElementData, SourceMetadata


class SearchResponse(BaseModel):
    """API response for /api/search endpoint."""
    query: str
    results: List[SearchResult]
    count: int
    metadata: SourceMetadata

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    """API response for /api/profile endpoint."""
    noc_code: str
    title: str
    key_activities: JDElementData
    skills: JDElementData
    effort: JDElementData
    responsibility: JDElementData
    working_conditions: JDElementData
    metadata: SourceMetadata

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """API error response."""
    error: str
    detail: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
