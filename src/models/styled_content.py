"""Styled content models for provenance tracking in Phase 12 generation.

This module defines models that link styled output to original NOC statements,
track individual generation attempts with metadata, and maintain version history
for audit trail and reversion capability.

Key models:
- GenerationAttempt: Single generation attempt with confidence and vocabulary audit
- StyledStatement: Styled variant with full provenance linking to source NOC
- StyleVersionHistory: Complete version history for reversion support
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict

from src.models.ai import StyleContentType
from src.models.vocabulary_audit import VocabularyAudit


class GenerationAttempt(BaseModel):
    """Single generation attempt record (PROV-05).

    Captures all metadata for one AI generation attempt, including the
    styled text, confidence score, vocabulary coverage, and acceptance status.

    Attributes:
        attempt_id: Unique identifier for this attempt (UUID)
        styled_text: The generated styled text
        confidence_score: AI confidence in generation quality (0.0-1.0)
        vocabulary_coverage: Percentage of content using NOC vocabulary
        vocabulary_audit: Detailed vocabulary validation results
        generated_at: Timestamp when generation occurred
        was_accepted: Whether user accepted this version as active
    """
    attempt_id: str = Field(default_factory=lambda: str(uuid4()))
    styled_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    vocabulary_coverage: float
    vocabulary_audit: VocabularyAudit
    generated_at: datetime
    was_accepted: bool = False

    model_config = ConfigDict(frozen=True)


class StyledStatement(BaseModel):
    """Styled variant with full provenance linking to source NOC (PROV-01, PROV-03).

    Links the styled output to its original NOC statement, preserving the original
    text alongside the styled variant for audit trail and transparency.

    Attributes:
        original_noc_statement_id: ID linking to source NOC statement (PROV-01)
        original_noc_text: Preserved original NOC text (PROV-03)
        styled_text: The styled variant text
        content_type: AI disclosure type (PROV-02)
        confidence_score: AI confidence in styling quality (0.0-1.0)
        retry_count: Number of generation attempts for this statement
        vocabulary_coverage: Percentage of content using NOC vocabulary
        vocabulary_audit: Detailed vocabulary validation results
        generated_at: Timestamp when styling occurred
        version_id: Unique identifier for this version
    """
    original_noc_statement_id: str
    original_noc_text: str
    styled_text: str
    content_type: StyleContentType
    confidence_score: float = Field(ge=0.0, le=1.0)
    retry_count: int = Field(ge=0, default=0)
    vocabulary_coverage: float
    vocabulary_audit: VocabularyAudit
    generated_at: datetime
    version_id: str

    model_config = ConfigDict(frozen=True)


class StyleVersionHistory(BaseModel):
    """Complete version history for a styled statement with reversion support.

    Tracks all generation attempts for a single NOC statement, allowing users
    to review and revert to any previous version. Per CONTEXT.md:
    - "Full version history tracked (all generated variants kept for audit)"
    - "Users can revert to any previous styled version from history"

    Not frozen because:
    - generation_attempts list grows as new versions are generated
    - active_version_index changes when user selects different version

    Version limit (e.g., 10 max) enforced in Phase 12 generation logic,
    not in this schema.

    Attributes:
        original_noc_statement_id: The source statement this history tracks
        original_noc_text: Preserved original NOC text
        generation_attempts: List of all generation attempts
        active_version_index: Index of currently active version (None if no accepted version)
    """
    original_noc_statement_id: str
    original_noc_text: str
    generation_attempts: List[GenerationAttempt] = Field(default_factory=list)
    active_version_index: Optional[int] = None
