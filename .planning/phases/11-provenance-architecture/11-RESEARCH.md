# Phase 11: Provenance Architecture - Research

**Researched:** 2026-02-03
**Domain:** Data provenance schema design, audit trail architecture, AI disclosure metadata
**Confidence:** HIGH

## Summary

This phase establishes the data model schema for styled content provenance, extending the existing `export_models.py` infrastructure. The research examined the existing codebase architecture (Pydantic models for export, vocabulary validation, OaSIS provenance mapping) and best practices for audit trail design, version history storage, and AI disclosure metadata.

The existing codebase already has a solid foundation with `SelectionMetadata`, `AIMetadata`, `StatementExport`, and OaSIS provenance tracking. This phase extends these models to support styled content with: (1) linkage between styled output and original NOC statement, (2) differentiated AI disclosure labels, (3) vocabulary audit metadata, (4) generation metadata with confidence scores, and (5) version history for reversion capability.

**Primary recommendation:** Extend `export_models.py` with new Pydantic models (`StyledStatement`, `VocabularyAudit`, `GenerationAttempt`, `StyleVersionHistory`) using frozen models for immutability where appropriate, and add a new `StyleContentType` enum to differentiate "AI-Styled" from "AI-Generated" content.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pydantic | 2.x (existing) | Data model validation and serialization | Already used throughout project; provides frozen models, nested validation, computed fields |
| Python dataclasses | stdlib | Lightweight frozen data structures | Supplement Pydantic for simple metadata carriers |
| datetime | stdlib | Timestamp handling | ISO 8601 compliance for audit timestamps |
| enum | stdlib | Type-safe disclosure labels | Enforces valid AI disclosure categories |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typing | stdlib | Type hints for schema | All model definitions |
| uuid | stdlib | Unique identifiers for version history | Generating statement version IDs |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pydantic frozen models | Python dataclass frozen=True | Pydantic already in use; provides richer validation |
| UUID for version IDs | Sequential integers | UUIDs are globally unique, avoid collision across sessions |
| List for version history | Dict keyed by timestamp | List preserves order naturally, easier to iterate |

**Installation:**
No new packages required - using existing stack.

## Architecture Patterns

### Recommended Model Structure

```
src/models/
├── export_models.py        # Existing - extend with styled content
├── styled_content.py       # NEW: Styled statement models
├── vocabulary_audit.py     # NEW: Vocabulary audit models
└── ai.py                   # Existing - extend with StyleContentType enum
```

### Pattern 1: Statement Linkage (Original -> Styled)

**What:** Each styled statement maintains explicit reference to its source NOC statement ID.
**When to use:** Every styled statement must link back to original.
**Example:**
```python
# Source: Existing pattern from export_models.py extended
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class StyleContentType(str, Enum):
    """Differentiated AI disclosure labels per PROV-02."""
    AI_STYLED = "ai_styled"       # Styled from NOC using JD samples
    AI_GENERATED = "ai_generated" # Synthesized content (e.g., overview)
    ORIGINAL_NOC = "original_noc" # Fallback to unmodified NOC

class StyledStatement(BaseModel):
    """Styled variant with full provenance linkage."""
    # Link to source
    original_noc_statement_id: str  # e.g., "key_activities-0"
    original_noc_text: str          # Preserved original text (PROV-03)

    # Styled output
    styled_text: str
    content_type: StyleContentType  # Disclosure label (PROV-02)

    # Generation metadata (PROV-05)
    confidence_score: float = Field(ge=0.0, le=1.0)
    retry_count: int = Field(ge=0, default=0)
    vocabulary_coverage: float = Field(ge=0.0, le=100.0)
    generated_at: datetime

    # Version tracking
    version_id: str  # UUID for this version

    model_config = {"frozen": True}  # Immutable once created
```

### Pattern 2: Vocabulary Audit Metadata

**What:** Each styled statement includes vocabulary validation results.
**When to use:** All styled statements to support PROV-04.
**Example:**
```python
from typing import List, Dict

class VocabularyTerm(BaseModel):
    """Individual term with category metadata."""
    term: str
    category: str  # "skill", "ability", "knowledge", "work_activity"
    is_noc_term: bool

class VocabularyAudit(BaseModel):
    """Vocabulary validation results for a styled statement."""
    noc_terms_used: List[VocabularyTerm]
    non_noc_terms: List[str]  # Words not in NOC vocabulary (edge cases)
    coverage_percentage: float
    total_content_words: int
    noc_word_count: int

    model_config = {"frozen": True}
```

### Pattern 3: Version History (Append-Only)

**What:** All generated variants stored for audit trail and reversion.
**When to use:** Track every generation attempt for full history.
**Example:**
```python
from typing import List
from uuid import uuid4

class GenerationAttempt(BaseModel):
    """Single generation attempt record."""
    attempt_id: str = Field(default_factory=lambda: str(uuid4()))
    styled_text: str
    confidence_score: float
    vocabulary_coverage: float
    vocabulary_audit: VocabularyAudit
    generated_at: datetime
    was_accepted: bool = False  # True if user selected this version

    model_config = {"frozen": True}

class StyleVersionHistory(BaseModel):
    """Complete version history for a single NOC statement."""
    original_noc_statement_id: str
    original_noc_text: str

    # Append-only list of all attempts
    generation_attempts: List[GenerationAttempt] = Field(default_factory=list)

    # Current active version (index into generation_attempts, or None for original)
    active_version_index: Optional[int] = None

    def get_active_version(self) -> Optional[GenerationAttempt]:
        """Get currently active styled version, or None if using original."""
        if self.active_version_index is not None:
            return self.generation_attempts[self.active_version_index]
        return None
```

### Pattern 4: Confidence Score Visual Indicators

**What:** Map confidence scores to color-coded indicators.
**When to use:** UI display of generation quality.
**Example:**
```python
from enum import Enum

class ConfidenceLevel(str, Enum):
    """Color-coded confidence levels for UI display."""
    HIGH = "green"    # >= 0.8
    MEDIUM = "yellow" # >= 0.5 and < 0.8
    LOW = "red"       # < 0.5

# Threshold constants
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,   # GREEN: High confidence, likely acceptable
    "medium": 0.5, # YELLOW: Review recommended
    "low": 0.0     # RED: Low confidence, manual review required
}

def get_confidence_level(score: float) -> ConfidenceLevel:
    """Map numeric confidence to color indicator."""
    if score >= CONFIDENCE_THRESHOLDS["high"]:
        return ConfidenceLevel.HIGH
    elif score >= CONFIDENCE_THRESHOLDS["medium"]:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW
```

### Anti-Patterns to Avoid

- **Mutable audit records:** Never allow modification of generation attempt records after creation. Use frozen models.
- **Losing original text:** Always preserve the original NOC statement text, not just the ID reference.
- **Implicit disclosure:** Never leave AI involvement ambiguous. Every statement must have explicit `content_type`.
- **Discarding failed attempts:** Keep all generation attempts including rejected ones for full audit trail.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Vocabulary validation | Custom word matching | Existing `VocabularyValidator` class | Already handles stop words, tokenization, case folding |
| Datetime serialization | Manual string formatting | Pydantic datetime fields with existing validators | Already implemented in `parse_flexible_datetime()` |
| OaSIS provenance lookup | Hardcoded URLs | Existing `oasis_provenance.py` utilities | Already maps source attributes to table metadata |
| Statement ID generation | Custom ID scheme | Follow existing pattern `{jd_element}-{index}` | Consistency with `SelectionMetadata.id` format |

**Key insight:** The existing codebase has robust patterns for provenance tracking, datetime handling, and vocabulary validation. Extend these rather than creating parallel systems.

## Common Pitfalls

### Pitfall 1: Losing Provenance Chain During Export

**What goes wrong:** Styled statements lose their link to original NOC statements when exported to PDF/DOCX.
**Why it happens:** Export logic transforms data and drops metadata fields not needed for display.
**How to avoid:** Ensure `ExportData` model includes styled statement metadata; export templates render footnotes with original NOC text.
**Warning signs:** Exports lack "Original NOC" footnotes; compliance sections missing styled content disclosure.

### Pitfall 2: Vocabulary Category Not Tracked

**What goes wrong:** Vocabulary audit shows terms but not which NOC category (skill/ability/knowledge/work activity).
**Why it happens:** Current `VocabularyIndex` doesn't track which parquet file a term came from.
**How to avoid:** Extend `VocabularyIndex` or create parallel category lookup; store category with each term.
**Warning signs:** Vocabulary audit shows boolean is_noc_term but no category breakdown.

### Pitfall 3: Version History Grows Unbounded

**What goes wrong:** No limit on generation attempts causes memory/storage issues over long sessions.
**Why it happens:** Append-only pattern without any cleanup strategy.
**How to avoid:** Set reasonable limit (e.g., 10 versions per statement); oldest non-accepted versions can be pruned.
**Warning signs:** Session state grows large; performance degrades during export.

### Pitfall 4: Confidence Score Miscalibration

**What goes wrong:** Color indicators don't match actual quality; users lose trust in the system.
**Why it happens:** Threshold values set arbitrarily without validation against real outputs.
**How to avoid:** Start with documented thresholds (0.8/0.5); plan for adjustment based on Phase 12 testing.
**Warning signs:** High-confidence (green) outputs frequently rejected by users; low-confidence (red) outputs often acceptable.

## Code Examples

Verified patterns from existing codebase:

### Extending SelectionMetadata for Styled Content

```python
# Source: Based on existing export_models.py SelectionMetadata
class StyledSelectionMetadata(BaseModel):
    """Selection with optional styled variant and full provenance."""
    # Existing fields from SelectionMetadata
    id: str
    text: str  # Original NOC text (always preserved)
    jd_element: str
    source_attribute: str
    source_url: Optional[str] = None
    selected_at: datetime
    description: Optional[str] = None
    proficiency: Optional[ProficiencyData] = None
    publication_date: Optional[str] = None
    source_table_url: Optional[str] = None

    # NEW: Styled content fields
    styled_variant: Optional[StyledStatement] = None
    version_history: Optional[StyleVersionHistory] = None

    model_config = ConfigDict(from_attributes=True)
```

### AI Disclosure Label Constants

```python
# Source: Derived from CONTEXT.md decisions
AI_DISCLOSURE_LABELS = {
    StyleContentType.AI_STYLED: "AI-Styled using Job Description Samples",
    StyleContentType.AI_GENERATED: "AI-Generated",
    StyleContentType.ORIGINAL_NOC: "Original NOC",
}

def get_disclosure_label(content_type: StyleContentType) -> str:
    """Get human-readable disclosure label for display."""
    return AI_DISCLOSURE_LABELS.get(content_type, "Unknown")
```

### Vocabulary Audit Integration

```python
# Source: Extending existing VocabularyValidator pattern
from src.vocabulary.validator import VocabularyValidator

def build_vocabulary_audit(
    styled_text: str,
    validator: VocabularyValidator
) -> VocabularyAudit:
    """Build vocabulary audit metadata for a styled statement."""
    result = validator.validate_text(styled_text)

    # Note: Category tracking requires VocabularyIndex extension
    # For now, all terms marked as "unknown" category
    noc_terms = [
        VocabularyTerm(term=word, category="unknown", is_noc_term=True)
        for word in result.get("noc_words_list", [])  # Requires validator extension
    ]

    return VocabularyAudit(
        noc_terms_used=noc_terms,
        non_noc_terms=result["non_noc_words"],
        coverage_percentage=result["coverage_percentage"],
        total_content_words=result["total_words"],
        noc_word_count=result["noc_words"]
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single AI disclosure type | Differentiated labels (styled vs generated) | This phase | More granular compliance; different treatment for style transfer vs synthesis |
| Flat provenance | Hierarchical (statement -> styled -> attempts) | This phase | Full audit trail with reversion capability |
| Binary vocab validation | Category-aware vocab audit | This phase | Richer compliance reporting |

**Deprecated/outdated:**
- Single `ai_metadata` field: Will be replaced with per-statement `content_type` for styled content
- Vocabulary validation without categories: Needs extension to track skill/ability/knowledge/work_activity

## Open Questions

Things that couldn't be fully resolved:

1. **Vocabulary Category Tracking**
   - What we know: `VocabularyIndex` loads from 4 parquet files but doesn't track source file
   - What's unclear: How to efficiently track which category each term belongs to
   - Recommendation: Either extend `VocabularyIndex` with category lookup, or create parallel category mapping from parquet column names

2. **Version History Storage Limits**
   - What we know: Append-only is good for audit, but unbounded growth is problematic
   - What's unclear: Optimal limit for version history (5? 10? 20?)
   - Recommendation: Start with 10 versions; prune oldest non-accepted versions when limit reached

3. **Confidence Score Calculation Method**
   - What we know: Phase 12 will implement generation; confidence calculation is TBD
   - What's unclear: Whether confidence is vocabulary coverage, semantic similarity, or composite
   - Recommendation: Schema should accept any float 0-1; Phase 12 determines calculation method

## Sources

### Primary (HIGH confidence)
- Existing codebase analysis: `src/models/export_models.py`, `src/models/ai.py`, `src/vocabulary/validator.py`
- Pydantic documentation: https://docs.pydantic.dev/latest/concepts/models/ - frozen models, nested validation
- Project CONTEXT.md decisions: AI disclosure labels, audit trail structure, vocabulary audit display

### Secondary (MEDIUM confidence)
- [LLM Evaluation Metrics Guide](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation) - confidence score threshold patterns
- [AWS Data Provenance Guidance](https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/ag.dlm.8-improve-traceability-with-data-provenance-tracking.html) - traceability best practices
- [Pydantic Best Practices](https://dev.to/devasservice/best-practices-for-using-pydantic-in-python-2021) - model versioning patterns

### Tertiary (LOW confidence)
- WebSearch results on AI content disclosure - emerging patterns, not yet standardized
- General data provenance trends 2026 - directional guidance only

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing Pydantic infrastructure from project
- Architecture patterns: HIGH - Extending proven patterns from existing codebase
- Schema design: HIGH - Based on explicit CONTEXT.md decisions
- Confidence thresholds: MEDIUM - Reasonable defaults (0.8/0.5) but may need tuning
- Vocabulary categories: MEDIUM - Clear need, implementation approach TBD

**Research date:** 2026-02-03
**Valid until:** 30 days (stable domain, schema design)
