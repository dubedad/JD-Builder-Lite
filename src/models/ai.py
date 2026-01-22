"""AI generation models with provenance tracking."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class StatementInput(BaseModel):
    """Statement selected by manager for generation input."""
    id: str  # e.g., "key_activities-0"
    text: str
    source_attribute: str
    jd_element: str  # e.g., "key_activities"

    model_config = ConfigDict(from_attributes=True)


class JobContext(BaseModel):
    """Job context for generation prompt."""
    job_title: str
    noc_code: str
    noc_title: str
    occupation_code: Optional[str] = None  # Full code with .XX suffix

    model_config = ConfigDict(from_attributes=True)


class GenerationRequest(BaseModel):
    """Request payload for /api/generate endpoint."""
    statements: List[StatementInput]
    context: JobContext

    model_config = ConfigDict(from_attributes=True)


class GenerationMetadata(BaseModel):
    """Provenance data for AI generation - stored in session."""
    model: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    prompt_version: str
    input_statement_ids: List[str]
    modified: bool = False  # True if manager edited output

    model_config = ConfigDict(from_attributes=True)
