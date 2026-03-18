"""Vocabulary audit models for styled content provenance tracking.

This module defines data types for tracking NOC vocabulary usage in styled content,
including vocabulary terms with category metadata, audit results with coverage metrics,
and confidence level indicators for visual display.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict


class ConfidenceLevel(str, Enum):
    """Visual indicator levels for confidence scores.

    HIGH (green): >= 0.8 confidence
    MEDIUM (yellow): >= 0.5 and < 0.8 confidence
    LOW (red): < 0.5 confidence
    """
    HIGH = "green"
    MEDIUM = "yellow"
    LOW = "red"


CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.5,
    "low": 0.0
}
"""Threshold values for confidence level determination.

- high: >= 0.8 maps to ConfidenceLevel.HIGH (green)
- medium: >= 0.5 maps to ConfidenceLevel.MEDIUM (yellow)
- low: >= 0.0 maps to ConfidenceLevel.LOW (red)
"""


class VocabularyTerm(BaseModel):
    """Individual vocabulary term with category metadata.

    Attributes:
        term: The vocabulary term string
        category: NOC category (skill, ability, knowledge, work_activity)
        is_noc_term: Whether the term exists in NOC vocabulary
    """
    term: str
    category: str
    is_noc_term: bool

    model_config = ConfigDict(frozen=True)


class VocabularyAudit(BaseModel):
    """Vocabulary validation results for styled content (per PROV-04).

    Tracks NOC vocabulary usage in styled content, aligning with
    VocabularyValidator.validate_text() output structure.

    Attributes:
        noc_terms_used: List of NOC terms found in content with metadata
        non_noc_terms: List of terms not found in NOC vocabulary
        coverage_percentage: Percentage of content words from NOC vocabulary
        total_content_words: Total word count excluding stop words
        noc_word_count: Count of words matching NOC vocabulary
    """
    noc_terms_used: List[VocabularyTerm]
    non_noc_terms: List[str]
    coverage_percentage: float
    total_content_words: int
    noc_word_count: int

    model_config = ConfigDict(frozen=True)
